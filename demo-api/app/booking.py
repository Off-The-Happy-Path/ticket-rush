"""Booking rules: who gets which seat. The overselling bug lives in reserve_seat()."""
import asyncio
import secrets
from datetime import timedelta

from app.clock import now
from app.config import settings
from app.errors import AppError
from app.models import (Event, Order, OrderRequest, Reservation, ReservationRequest,
                        ReservationStatus, Seat, SeatStatus)
from app.storage import store


async def reserve_seat(request: ReservationRequest) -> Reservation:
    event = await get_event_or_404(request.event_id)
    if now() < event.on_sale_at:
        raise AppError(403, "sale_not_open", f"Sale opens at {event.on_sale_at:%Y-%m-%dT%H:%M:%SZ}")

    if settings.oversell_bug:
        return await _check_and_hold(request)       # BUG: no lock, two fans can pass the check

    async with store.seat_lock(request.event_id, request.seat_id):
        return await _check_and_hold(request)


async def _check_and_hold(request: ReservationRequest) -> Reservation:
    seat = await get_seat_or_404(request.event_id, request.seat_id)
    if seat.status_at(now()) != SeatStatus.AVAILABLE:
        raise AppError(409, "seat_not_available", f"Seat {seat.seat_id} is not available")

    await simulated_db_round_trip()                 # the race window

    reservation = Reservation(
        id=new_id("res"),
        event_id=seat.event_id,
        seat_id=seat.seat_id,
        customer_id=request.customer_id,
        status=ReservationStatus.ACTIVE,
        expires_at=now() + timedelta(seconds=settings.hold_seconds),
    )
    seat.status = SeatStatus.HELD
    seat.held_until = reservation.expires_at
    await store.save_seat(seat)
    await store.save_reservation(reservation)
    return reservation


async def place_order(request: OrderRequest) -> Order:
    reservation = await store.get_reservation(request.reservation_id)
    if reservation is None:
        raise AppError(404, "reservation_not_found", f"Reservation {request.reservation_id} does not exist")

    # Locked so a double-clicked "Pay" button cannot create two orders.
    async with store.seat_lock(reservation.event_id, reservation.seat_id):
        if reservation.status == ReservationStatus.ORDERED:
            raise AppError(409, "reservation_already_ordered", f"Reservation {reservation.id} is already paid")
        if now() >= reservation.expires_at:
            raise AppError(410, "reservation_expired", f"Reservation {reservation.id} expired")

        event = await get_event_or_404(reservation.event_id)
        await simulated_payment()

        order = Order(
            id=new_id("ord"),
            reservation_id=reservation.id,
            event_id=reservation.event_id,
            seat_id=reservation.seat_id,
            customer_id=reservation.customer_id,
            amount_cents=event.price_cents,
            created_at=now(),
        )
        reservation.status = ReservationStatus.ORDERED
        seat = await get_seat_or_404(reservation.event_id, reservation.seat_id)
        seat.status = SeatStatus.SOLD
        seat.held_until = None
        await store.save_reservation(reservation)
        await store.save_seat(seat)
        await store.save_order(order)
        return order


async def get_order_or_404(order_id: str) -> Order:
    order = await store.get_order(order_id)
    if order is None:
        raise AppError(404, "order_not_found", f"Order {order_id} does not exist")
    return order


async def get_event_or_404(event_id: int) -> Event:
    event = await store.get_event(event_id)
    if event is None:
        raise AppError(404, "event_not_found", f"Event {event_id} does not exist")
    return event


async def get_seat_or_404(event_id: int, seat_id: str) -> Seat:
    seat = await store.get_seat(event_id, seat_id)
    if seat is None:
        raise AppError(404, "seat_not_found", f"Seat {seat_id} does not exist")
    return seat


def new_id(prefix: str) -> str:
    return f"{prefix}_{secrets.token_hex(6)}"


async def simulated_db_round_trip() -> None:
    await asyncio.sleep(settings.db_latency_ms / 1000)


async def simulated_payment() -> None:
    await asyncio.sleep(settings.payment_latency_ms / 1000)

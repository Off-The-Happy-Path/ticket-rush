"""Keeps everything in Python dicts. Data is gone after a restart, which is fine for a demo."""
import asyncio
from collections import defaultdict

from app.models import Event, Order, Reservation, Seat


class InMemoryStore:
    def __init__(self) -> None:
        self.events: dict[int, Event] = {}
        self.seats: dict[int, dict[str, Seat]] = {}
        self.reservations: dict[str, Reservation] = {}
        self.orders: dict[str, Order] = {}
        self.locks: defaultdict[tuple[int, str], asyncio.Lock] = defaultdict(asyncio.Lock)

    async def reset(self, events: list[Event], seats: list[Seat]) -> None:
        self.events = {event.id: event for event in events}
        self.seats = {event.id: {} for event in events}
        for seat in seats:
            self.seats[seat.event_id][seat.seat_id] = seat
        self.reservations = {}
        self.orders = {}
        self.locks = defaultdict(asyncio.Lock)

    async def list_events(self) -> list[Event]:
        return list(self.events.values())

    async def get_event(self, event_id: int) -> Event | None:
        return self.events.get(event_id)

    async def list_seats(self, event_id: int) -> list[Seat]:
        return list(self.seats.get(event_id, {}).values())

    async def get_seat(self, event_id: int, seat_id: str) -> Seat | None:
        return self.seats.get(event_id, {}).get(seat_id)

    async def save_seat(self, seat: Seat) -> None:
        self.seats[seat.event_id][seat.seat_id] = seat

    async def get_reservation(self, reservation_id: str) -> Reservation | None:
        return self.reservations.get(reservation_id)

    async def save_reservation(self, reservation: Reservation) -> None:
        self.reservations[reservation.id] = reservation

    async def get_order(self, order_id: str) -> Order | None:
        return self.orders.get(order_id)

    async def save_order(self, order: Order) -> None:
        self.orders[order.id] = order

    async def list_orders(self, event_id: int) -> list[Order]:
        return [order for order in self.orders.values() if order.event_id == event_id]

    def seat_lock(self, event_id: int, seat_id: str) -> asyncio.Lock:
        return self.locks[(event_id, seat_id)]

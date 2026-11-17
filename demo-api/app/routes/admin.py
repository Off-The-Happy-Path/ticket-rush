"""Test helpers. Mounted only when ADMIN_ENABLED=true. Real systems never expose these."""
import time
from collections import defaultdict

from fastapi import APIRouter

from app.models import EventReport, OversoldSeat, Report, ResetRequest, ResetResult
from app.clock import now
from app.faults import fault_log
from app.seed import load_seed
from app.storage import store

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/reset", response_model=ResetResult)
async def reset(request: ResetRequest | None = None) -> ResetResult:
    opens_in = request.sale_opens_in_seconds if request else 0
    events, seats = await load_seed(opens_in)
    fault_log.reset()
    return ResetResult(events=len(events), seats=len(seats), sale_opens_at=events[0].on_sale_at)


@router.get("/report", response_model=Report)
async def report() -> Report:
    event_reports = []
    for event in await store.list_events():
        orders = await store.list_orders(event.id)
        orders_by_seat: defaultdict[str, list[str]] = defaultdict(list)
        for order in orders:
            orders_by_seat[order.seat_id].append(order.id)

        oversold_seats = [
            OversoldSeat(seat_id=seat_id, times_sold=len(order_ids), order_ids=order_ids)
            for seat_id, order_ids in orders_by_seat.items()
            if len(order_ids) > 1
        ]
        reservations_by_fan: defaultdict[str, int] = defaultdict(int)
        for reservation in await store.list_reservations(event.id):
            reservations_by_fan[reservation.customer_id] += 1
        orders_by_fan: defaultdict[str, int] = defaultdict(int)
        for order in orders:
            orders_by_fan[order.customer_id] += 1
        extra_holds = sum(n - 1 for n in reservations_by_fan.values() if n > 1)
        extra_orders = sum(n - 1 for n in orders_by_fan.values() if n > 1)
        taken = sum(1 for s in await store.list_seats(event.id) if s.status_at(now()).value != "available")
        event_reports.append(EventReport(
            event_id=event.id,
            capacity=event.capacity,
            orders_confirmed=len(orders),
            unique_seats_sold=len(orders_by_seat),
            duplicate_sales=len(orders) - len(orders_by_seat),
            oversold_seats=oversold_seats,
            seats_unavailable=taken,
            retried_duplicates=extra_holds + extra_orders,
            fans_with_duplicate_holds=sum(1 for n in reservations_by_fan.values() if n > 1),
            fans_with_duplicate_orders=sum(1 for n in orders_by_fan.values() if n > 1),
        ))
    return Report(
        events=event_reports,
        duplicate_sales_total=sum(r.duplicate_sales for r in event_reports),
        retried_duplicates_total=sum(r.retried_duplicates for r in event_reports),
        responses_dropped_after_commit=len(fault_log.dropped),
        dropped_responses=list(fault_log.dropped),
    )


@router.post("/freeze")
async def freeze(seconds: float = 3) -> dict:
    time.sleep(seconds)    # a blocking call in async code: the whole API stops answering
    return {"frozen_for": seconds}

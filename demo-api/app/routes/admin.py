"""Test helpers. Mounted only when ADMIN_ENABLED=true. Real systems never expose these."""
from collections import defaultdict

from fastapi import APIRouter

from app.models import EventReport, OversoldSeat, Report, ResetRequest, ResetResult
from app.seed import load_seed
from app.storage import store

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/reset", response_model=ResetResult)
async def reset(request: ResetRequest | None = None) -> ResetResult:
    opens_in = request.sale_opens_in_seconds if request else 0
    events, seats = await load_seed(opens_in)
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
        event_reports.append(EventReport(
            event_id=event.id,
            capacity=event.capacity,
            orders_confirmed=len(orders),
            unique_seats_sold=len(orders_by_seat),
            duplicate_sales=len(orders) - len(orders_by_seat),
            oversold_seats=oversold_seats,
        ))
    return Report(
        events=event_reports,
        duplicate_sales_total=sum(r.duplicate_sales for r in event_reports),
    )

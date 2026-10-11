from fastapi import APIRouter

from app.booking import get_event_or_404
from app.clock import now
from app.models import ErrorResponse, EventOut, SeatMap, SeatOut, SeatStatus
from app.storage import store

router = APIRouter(tags=["events"])


@router.get("/events", response_model=list[EventOut])
async def list_events() -> list[EventOut]:
    current = now()
    result = []
    for event in await store.list_events():
        seats = await store.list_seats(event.id)
        available = sum(1 for seat in seats if seat.status_at(current) == SeatStatus.AVAILABLE)
        result.append(EventOut(**event.model_dump(), seats_available=available))
    return result


@router.get(
    "/events/{event_id}/seats",
    response_model=SeatMap,
    responses={404: {"model": ErrorResponse}},
)
async def get_seat_map(event_id: int, status: SeatStatus | None = None) -> SeatMap:
    event = await get_event_or_404(event_id)
    current = now()
    seats = [
        SeatOut(seat_id=seat.seat_id, row=seat.row, number=seat.number, status=seat.status_at(current))
        for seat in await store.list_seats(event.id)
    ]
    if status is not None:
        seats = [seat for seat in seats if seat.status == status]
    return SeatMap(event_id=event.id, seats=seats)

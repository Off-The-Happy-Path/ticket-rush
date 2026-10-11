from fastapi import APIRouter

from app.booking import reserve_seat
from app.models import ErrorResponse, Reservation, ReservationRequest

router = APIRouter(tags=["reservations"])


@router.post(
    "/reservations",
    response_model=Reservation,
    status_code=201,
    responses={
        403: {"model": ErrorResponse, "description": "Sale not open yet"},
        404: {"model": ErrorResponse, "description": "Event or seat not found"},
        409: {"model": ErrorResponse, "description": "Seat not available"},
    },
)
async def create_reservation(request: ReservationRequest) -> Reservation:
    return await reserve_seat(request)

from fastapi import APIRouter

from app.booking import get_order_or_404, place_order
from app.models import ErrorResponse, Order, OrderRequest

router = APIRouter(tags=["orders"])


@router.post(
    "/orders",
    response_model=Order,
    status_code=201,
    responses={
        404: {"model": ErrorResponse, "description": "Reservation not found"},
        409: {"model": ErrorResponse, "description": "Reservation already paid"},
        410: {"model": ErrorResponse, "description": "Reservation expired"},
    },
)
async def create_order(request: OrderRequest) -> Order:
    return await place_order(request)


@router.get("/orders/{order_id}", response_model=Order, responses={404: {"model": ErrorResponse}})
async def get_order(order_id: str) -> Order:
    return await get_order_or_404(order_id)

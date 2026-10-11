"""Request and response shapes: the API contract."""
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class SeatStatus(StrEnum):
    AVAILABLE = "available"
    HELD = "held"
    SOLD = "sold"


class ReservationStatus(StrEnum):
    ACTIVE = "active"
    ORDERED = "ordered"


class Event(BaseModel):
    id: int
    name: str
    venue: str
    starts_at: datetime
    on_sale_at: datetime
    price_cents: int
    capacity: int


class EventOut(Event):
    seats_available: int


class Seat(BaseModel):
    event_id: int
    seat_id: str
    row: str
    number: int
    status: SeatStatus = SeatStatus.AVAILABLE
    held_until: datetime | None = None

    def status_at(self, now: datetime) -> SeatStatus:
        """A hold that has run out counts as available again."""
        if self.status == SeatStatus.HELD and self.held_until <= now:
            return SeatStatus.AVAILABLE
        return self.status


class SeatOut(BaseModel):
    seat_id: str
    row: str
    number: int
    status: SeatStatus


class SeatMap(BaseModel):
    event_id: int
    seats: list[SeatOut]


class ReservationRequest(BaseModel):
    event_id: int
    seat_id: str = Field(min_length=1, max_length=10)
    customer_id: str = Field(min_length=1, max_length=64)


class Reservation(BaseModel):
    id: str
    event_id: int
    seat_id: str
    customer_id: str
    status: ReservationStatus
    expires_at: datetime


class OrderRequest(BaseModel):
    reservation_id: str = Field(min_length=1, max_length=64)


class Order(BaseModel):
    id: str
    reservation_id: str
    event_id: int
    seat_id: str
    customer_id: str
    amount_cents: int
    status: Literal["confirmed"] = "confirmed"
    created_at: datetime


class ErrorResponse(BaseModel):
    error: str
    message: str


class Health(BaseModel):
    status: Literal["ok"] = "ok"
    oversell_bug: bool
    admin_enabled: bool


# --- Admin only (hidden from /docs) ---

class ResetRequest(BaseModel):
    sale_opens_in_seconds: int = Field(default=0, ge=0, le=86_400)


class ResetResult(BaseModel):
    status: Literal["reset"] = "reset"
    events: int
    seats: int
    sale_opens_at: datetime


class OversoldSeat(BaseModel):
    seat_id: str
    times_sold: int
    order_ids: list[str]


class EventReport(BaseModel):
    """Always true: orders_confirmed == unique_seats_sold + duplicate_sales."""
    event_id: int
    capacity: int                       # seats in the venue
    orders_confirmed: int               # tickets sold, counting every order
    unique_seats_sold: int              # different seats with at least one order
    duplicate_sales: int                # orders for a seat someone already bought
    oversold_seats: list[OversoldSeat]  # seats with more than one order


class Report(BaseModel):
    events: list[EventReport]
    duplicate_sales_total: int

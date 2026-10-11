"""Demo data: three fictional concerts. Event 1 is the small, sold-out-in-seconds show."""
from datetime import datetime, timedelta
from string import ascii_uppercase

from app.clock import now
from app.models import Event, Seat
from app.storage import store

CONCERTS = [
    # name, venue, days until show, price in cents, rows, seats per row
    ("Neon Harbor Live", "Riverside Arena", 30, 8900, 6, 20),
    ("The Paper Satellites", "Union Hall", 45, 4500, 10, 50),
    ("Velvet Static Tour", "Northgate Stadium", 60, 12900, 20, 50),
]


def build_seed(today: datetime, sale_opens_at: datetime) -> tuple[list[Event], list[Seat]]:
    events: list[Event] = []
    seats: list[Seat] = []
    for event_id, (name, venue, days, price, rows, per_row) in enumerate(CONCERTS, start=1):
        show_day = today + timedelta(days=days)
        events.append(Event(
            id=event_id,
            name=name,
            venue=venue,
            starts_at=show_day.replace(hour=20, minute=0, second=0),
            on_sale_at=sale_opens_at,
            price_cents=price,
            capacity=rows * per_row,
        ))
        for row in ascii_uppercase[:rows]:
            for number in range(1, per_row + 1):
                seats.append(Seat(event_id=event_id, seat_id=f"{row}-{number}", row=row, number=number))
    return events, seats


async def load_seed(sale_opens_in_seconds: int = 0) -> tuple[list[Event], list[Seat]]:
    """Reset all data. By default every sale is already open."""
    today = now()
    events, seats = build_seed(today, today + timedelta(seconds=sale_opens_in_seconds))
    await store.reset(events, seats)
    return events, seats

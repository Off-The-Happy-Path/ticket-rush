"""Two fans click Buy on the same seat at the same moment."""
import asyncio

import httpx
import pytest

from app.config import settings
from app.main import create_app
from app.seed import load_seed


async def two_fans_buy_seat_a1() -> tuple[list[int], dict]:
    await load_seed()
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        async def buy(fan: str) -> int:
            body = {"event_id": 1, "seat_id": "A-1", "customer_id": fan}
            reservation = await client.post("/reservations", json=body)
            if reservation.status_code == 201:
                await client.post("/orders", json={"reservation_id": reservation.json()["id"]})
            return reservation.status_code

        statuses = await asyncio.gather(buy("fan-1"), buy("fan-2"))
        report = (await client.get("/admin/report")).json()
    return sorted(statuses), report


@pytest.mark.parametrize("bug_on, expected_statuses, expected_duplicates", [
    (False, [201, 409], 0),
    (True, [201, 201], 1),
])
def test_same_seat_race(monkeypatch, bug_on, expected_statuses, expected_duplicates):
    monkeypatch.setattr(settings, "oversell_bug", bug_on)
    monkeypatch.setattr(settings, "db_latency_ms", 20)

    statuses, report = asyncio.run(two_fans_buy_seat_a1())

    assert statuses == expected_statuses
    assert report["duplicate_sales_total"] == expected_duplicates


def test_report_numbers_add_up(monkeypatch):
    monkeypatch.setattr(settings, "oversell_bug", True)
    monkeypatch.setattr(settings, "db_latency_ms", 20)

    _, report = asyncio.run(two_fans_buy_seat_a1())
    event = report["events"][0]

    assert event["orders_confirmed"] == event["unique_seats_sold"] + event["duplicate_sales"]
    assert event["oversold_seats"] == [
        {"seat_id": "A-1", "times_sold": 2, "order_ids": event["oversold_seats"][0]["order_ids"]}
    ]

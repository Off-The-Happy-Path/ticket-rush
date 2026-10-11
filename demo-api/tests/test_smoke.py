from fastapi.testclient import TestClient

from app.config import settings
from app.main import create_app


def reserve(client, seat_id="A-1", customer_id="fan-1"):
    return client.post("/reservations", json={"event_id": 1, "seat_id": seat_id, "customer_id": customer_id})


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "oversell_bug": False, "admin_enabled": True}


def test_events_start_fully_available(client):
    events = client.get("/events").json()
    assert len(events) == 3
    assert all(event["seats_available"] == event["capacity"] for event in events)


def test_fan_can_reserve_and_buy_a_seat(client):
    reservation = reserve(client).json()
    order = client.post("/orders", json={"reservation_id": reservation["id"]})
    assert order.status_code == 201
    assert order.json()["status"] == "confirmed"

    order_id = order.json()["id"]
    assert client.get(f"/orders/{order_id}").json()["seat_id"] == "A-1"
    sold = client.get("/events/1/seats", params={"status": "sold"}).json()["seats"]
    assert [seat["seat_id"] for seat in sold] == ["A-1"]


def test_second_fan_cannot_reserve_a_held_seat(client):
    assert reserve(client, customer_id="fan-1").status_code == 201
    response = reserve(client, customer_id="fan-2")
    assert response.status_code == 409
    assert response.json()["error"] == "seat_not_available"


def test_reservation_cannot_be_paid_twice(client):
    reservation_id = reserve(client).json()["id"]
    client.post("/orders", json={"reservation_id": reservation_id})
    response = client.post("/orders", json={"reservation_id": reservation_id})
    assert response.status_code == 409
    assert response.json()["error"] == "reservation_already_ordered"


def test_expired_hold_frees_the_seat(client, monkeypatch):
    monkeypatch.setattr(settings, "hold_seconds", 0)
    reservation_id = reserve(client, customer_id="fan-1").json()["id"]

    response = client.post("/orders", json={"reservation_id": reservation_id})
    assert response.status_code == 410
    assert reserve(client, customer_id="fan-2").status_code == 201


def test_cannot_reserve_before_sale_opens(client):
    client.post("/admin/reset", json={"sale_opens_in_seconds": 60})
    response = reserve(client)
    assert response.status_code == 403
    assert response.json()["error"] == "sale_not_open"


def test_unknown_seat_returns_404(client):
    response = reserve(client, seat_id="Z-99")
    assert response.status_code == 404
    assert response.json() == {"error": "seat_not_found", "message": "Seat Z-99 does not exist"}


def test_admin_endpoints_are_never_in_public_docs(client):
    assert not any(path.startswith("/admin") for path in client.get("/openapi.json").json()["paths"])


def test_admin_endpoints_do_not_exist_when_disabled(monkeypatch):
    monkeypatch.setattr(settings, "admin_enabled", False)
    with TestClient(create_app()) as client:
        assert client.get("/admin/report").status_code == 404

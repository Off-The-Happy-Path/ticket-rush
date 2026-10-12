import random

from locust import HttpUser, between, task


class Fan(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def browse_events(self):
        self.client.get("/events")

    @task(3)
    def check_seats(self):
        event_id = random.randint(1, 3)
        self.client.get(f"/events/{event_id}/seats", name="/events/[id]/seats")

    @task(1)
    def reserve_seat(self):
        seat = f"{random.choice('ABCDEFGHIJ')}-{random.randint(1, 50)}"
        body = {"event_id": 2, "seat_id": seat, "customer_id": "fan"}
        with self.client.post("/reservations", json=body, catch_response=True) as response:
            if response.status_code == 409:
                response.success()  # seat already taken: a normal answer, not an error

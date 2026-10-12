"""The 10:00 sale: every fan goes for the best seats of the 120-seat show.

Needs the API running with ADMIN_ENABLED=true. The test resets the data so the
sale opens a few seconds after it starts, and fails if any seat was sold twice.
"""
import logging
import random

import requests
from locust import HttpUser, between, events, task
from locust.exception import StopUser
from locust.runners import WorkerRunner

HOT_SHOW = 1
SALE_OPENS_IN_SECONDS = 15


class RushFan(HttpUser):
    wait_time = between(0.5, 1)

    @task
    def buy_best_seat(self):
        seats = self.client.get(
            f"/events/{HOT_SHOW}/seats", params={"status": "available"}, name="/events/[id]/seats"
        ).json()["seats"]
        if not seats:
            raise StopUser()                               # sold out: go home
        seat_id = random.choice(seats[:5])["seat_id"]      # everyone wants the front rows

        body = {"event_id": HOT_SHOW, "seat_id": seat_id, "customer_id": f"fan-{id(self)}"}
        with self.client.post("/reservations", json=body, catch_response=True) as reservation:
            if reservation.status_code in (403, 409):      # sale not open yet / seat just taken
                reservation.success()
                return

        if reservation.status_code == 201:
            self.client.post("/orders", json={"reservation_id": reservation.json()["id"]})
            raise StopUser()                               # got a ticket: done


@events.test_start.add_listener
def open_sale_soon(environment, **kwargs):
    if isinstance(environment.runner, WorkerRunner):
        return
    response = requests.post(
        f"{environment.host}/admin/reset", json={"sale_opens_in_seconds": SALE_OPENS_IN_SECONDS}
    )
    response.raise_for_status()


@events.test_stop.add_listener
def fail_if_oversold(environment, **kwargs):
    if isinstance(environment.runner, WorkerRunner):
        return
    report = requests.get(f"{environment.host}/admin/report").json()
    show = report["events"][HOT_SHOW - 1]
    logging.info("Sold %s tickets for %s seats", show["orders_confirmed"], show["capacity"])

    if report["duplicate_sales_total"] > 0:
        logging.error(
            "OVERSOLD: %s duplicate sales on %s seats",
            report["duplicate_sales_total"], len(show["oversold_seats"]),
        )
        environment.process_exit_code = 1

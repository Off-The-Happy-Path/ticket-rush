"""Steady traffic with one freeze: what does a load test report while the API is stuck?

Needs the API running with ADMIN_ENABLED=true. Thirty seconds into the test,
the API freezes for three seconds (POST /admin/freeze).
"""
import gevent
import requests
from locust import HttpUser, between, events, task
from locust.runners import WorkerRunner

FREEZE_AFTER_SECONDS = 30
FREEZE_SECONDS = 3


class Refresher(HttpUser):
    wait_time = between(0.3, 0.7)    # a page that asks "anything new?" about twice a second

    @task
    def list_events(self):
        self.client.get("/events")


@events.test_start.add_listener
def freeze_later(environment, **kwargs):
    if isinstance(environment.runner, WorkerRunner):
        return
    gevent.spawn_later(
        FREEZE_AFTER_SECONDS, requests.post,
        f"{environment.host}/admin/freeze", params={"seconds": FREEZE_SECONDS},
    )

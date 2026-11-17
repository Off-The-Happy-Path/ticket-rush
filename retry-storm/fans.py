"""Retry-storm harness: N fans buy one ticket each, with retries and backoff, NO idempotency key.

Each fan: POST /reservations, then POST /orders for the reservation they got.
Retry policy (the "safe" one everybody writes): up to 3 attempts per call, retry on
timeout or connection error only, wait 0.5s * 2^(attempt-1) plus a small seeded jitter.
If the server answers 409 "seat not available", the fan moves on to their next seat.
"""
import argparse
import asyncio
import json
import random
import time
from datetime import datetime, timezone

import httpx

EVENT_ID = 3          # Velvet Static Tour, 1000 seats: no sell-out noise in the numbers
ATTEMPTS = 3
BASE_DELAY = 0.5


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class Fan:
    def __init__(self, idx, seats, client, args, timeline):
        self.id = f"fan-{idx:03d}"
        self.seats = seats
        self.client = client
        self.args = args
        self.timeline = timeline
        self.rng = random.Random(f"{args.seed}:{self.id}")
        self.calls = []       # one dict per HTTP attempt
        self.reservations_seen = []
        self.order_seen = None

    def note(self, text):
        self.timeline.append({"at": stamp(), "fan": self.id, "src": "client", "text": text})

    async def call(self, path, body, label):
        """POST with retry-on-timeout. Returns (response or None, attempts used)."""
        for attempt in range(1, ATTEMPTS + 1):
            t0 = time.perf_counter()
            try:
                resp = await self.client.post(path, json=body, timeout=self.args.timeout)
                ms = round((time.perf_counter() - t0) * 1000)
                self.calls.append({"path": path, "attempt": attempt, "outcome": resp.status_code, "ms": ms})
                self.note(f"{label} attempt {attempt}: HTTP {resp.status_code} in {ms} ms")
                return resp, attempt
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                ms = round((time.perf_counter() - t0) * 1000)
                self.calls.append({"path": path, "attempt": attempt, "outcome": "timeout", "ms": ms})
                self.note(f"{label} attempt {attempt}: TIMEOUT after {ms} ms ({type(exc).__name__})")
                if attempt == ATTEMPTS:
                    break
                delay = BASE_DELAY * 2 ** (attempt - 1) + self.rng.uniform(0, 0.1)
                self.calls[-1]["backoff_s"] = round(delay, 3)
                self.note(f"{label} backing off {delay:.3f} s")
                await asyncio.sleep(delay)
        return None, ATTEMPTS

    async def run(self):
        reservation = None
        for seat in self.seats:
            resp, _ = await self.call("/reservations",
                                      {"event_id": EVENT_ID, "seat_id": seat, "customer_id": self.id},
                                      f"reserve {seat}")
            if resp is not None and resp.status_code == 201:
                reservation = resp.json()
                self.reservations_seen.append(reservation["id"])
                break
            if resp is not None and resp.status_code == 409:
                self.note(f"seat {seat} taken, trying the next seat")
                continue
            break                                  # gave up after timeouts
        if reservation is None:
            self.note("GAVE UP: could not reserve")
            return "gave_up_reserve"

        resp, _ = await self.call("/orders", {"reservation_id": reservation["id"]}, f"pay {reservation['id']}")
        if resp is not None and resp.status_code == 201:
            self.order_seen = resp.json()["id"]
            self.note(f"CONFIRMED order {self.order_seen} for seat {reservation['seat_id']}")
            return "confirmed"
        self.note("GAVE UP: could not pay" if resp is None else f"GAVE UP: pay answered {resp.status_code}")
        return "gave_up_pay"


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="http://127.0.0.1:8000")
    p.add_argument("--fans", type=int, default=100)
    p.add_argument("--timeout", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    limits = httpx.Limits(max_connections=args.fans + 10)
    async with httpx.AsyncClient(base_url=args.base, limits=limits) as client:
        await client.post("/admin/reset")
        seats = [s["seat_id"] for s in (await client.get(f"/events/{EVENT_ID}/seats")).json()["seats"]]
        timeline = []
        fans = [Fan(i, [seats[i], seats[i + args.fans], seats[i + 2 * args.fans]], client, args, timeline)
                for i in range(args.fans)]
        outcomes = await asyncio.gather(*(f.run() for f in fans))
        report = (await client.get("/admin/report")).json()

    result = {
        "args": vars(args), "attempts": ATTEMPTS, "base_delay_s": BASE_DELAY,
        "fans": [{"id": f.id, "outcome": o, "calls": f.calls, "reservations_seen": f.reservations_seen,
                  "order_seen": f.order_seen} for f, o in zip(fans, outcomes)],
        "timeline": sorted(timeline, key=lambda e: e["at"]),
        "report": report,
    }
    with open(args.out, "w") as fh:
        json.dump(result, fh, indent=1)


asyncio.run(main())

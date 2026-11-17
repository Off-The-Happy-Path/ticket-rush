"""Fault injection: the write commits, then the response never reaches the client.

DROP_RESPONSE_AFTER_COMMIT_PCT (0-100, default 0 = off) applies to POST /reservations and
POST /orders. The handler runs to the end and commits. Then, for that percentage of
successful writes, the middleware holds the response until the client gives up
(disconnects) instead of sending it. The client sees a timeout. The server has the data.

Which requests are dropped is deterministic: it depends on DROP_SEED, the path, the fan
and how many times that fan has called that path. It does not depend on how requests
from different fans interleave, so a seeded run reproduces.
"""
import asyncio
import hashlib
import json
import logging
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.config import settings
from app.storage import store

TARGETS = {"/reservations", "/orders"}

log = logging.getLogger("ticket_rush.faults")
if not log.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    log.propagate = False


@dataclass
class FaultLog:
    calls: defaultdict = field(default_factory=lambda: defaultdict(int))
    dropped: list[dict] = field(default_factory=list)

    def reset(self) -> None:
        self.calls.clear()
        self.dropped.clear()


fault_log = FaultLog()


def should_drop(path: str, fan: str, pct: int, seed: int) -> bool:
    key = (path, fan)
    fault_log.calls[key] += 1
    digest = hashlib.sha256(f"{seed}:{path}:{fan}:{fault_log.calls[key]}".encode()).digest()
    return int.from_bytes(digest[:4], "big") % 100 < pct


class DropResponseAfterCommit:
    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send):
        pct = settings.drop_response_after_commit_pct
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"] not in TARGETS or pct <= 0:
            return await self.app(scope, receive, send)

        # Read the request body once, then replay it to the app.
        chunks, more = [], True
        while more:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunks.append(message.get("body", b""))
            more = message.get("more_body", False)
        raw = b"".join(chunks)
        replayed = False

        async def replay():
            nonlocal replayed
            if not replayed:
                replayed = True
                return {"type": "http.request", "body": raw, "more_body": False}
            return await receive()

        # Buffer the response so we can decide whether to send it.
        buffered: list[dict] = []

        async def capture(message):
            buffered.append(message)

        await self.app(scope, replay, capture)
        start = next((m for m in buffered if m["type"] == "http.response.start"), None)
        body = b"".join(m.get("body", b"") for m in buffered if m["type"] == "http.response.body")

        if start and start["status"] == 201:                     # the write committed
            created = json.loads(body)
            fan = created.get("customer_id")
            if fan is None:                                       # an order: look the fan up
                reservation = await store.get_reservation(created["reservation_id"])
                fan = reservation.customer_id if reservation else "unknown"
            if should_drop(scope["path"], fan, pct, settings.drop_seed):
                record = {"at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                          "path": scope["path"], "fan": fan, "id": created["id"],
                          "seat_id": created["seat_id"]}
                fault_log.dropped.append(record)
                log.info("%s COMMITTED POST %s id=%s fan=%s seat=%s -> response dropped",
                         record["at"], scope["path"], created["id"], fan, created["seat_id"])
                await self._hold_until_client_gives_up(receive)
                return

        for message in buffered:
            await send(message)

    async def _hold_until_client_gives_up(self, receive) -> None:
        async def wait_for_disconnect():
            while (await receive())["type"] != "http.disconnect":
                pass
        try:
            await asyncio.wait_for(wait_for_disconnect(), settings.drop_hold_seconds)
        except asyncio.TimeoutError:
            pass

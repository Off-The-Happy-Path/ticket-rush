"""Turn results/pct-<N>.json into the numbers for the episode. Reads only real run output."""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def summarize(path: Path) -> dict:
    r = json.loads(path.read_text())
    fans, rep = r["fans"], r["report"]
    ev = next(e for e in rep["events"] if e["event_id"] == 3)
    calls = [(f["id"], c) for f in fans for c in f["calls"]]
    timeouts = [(fid, c) for fid, c in calls if c["outcome"] == "timeout"]
    dropped = Counter((d["fan"], d["path"]) for d in rep["dropped_responses"])
    seen_timeouts = Counter((fid, c["path"]) for fid, c in timeouts)
    committed_timeouts = sum(min(n, dropped[k]) for k, n in seen_timeouts.items())
    non_201 = [(fid, c) for fid, c in calls if c["outcome"] != 201]
    gave_up = [f for f in fans if f["outcome"] != "confirmed"]
    # server truth per fan: what the client saw as 201 plus what was dropped
    committed_by_fan = defaultdict(int)
    for f in fans:
        committed_by_fan[f["id"]] += len(f["reservations_seen"]) + (1 if f["order_seen"] else 0)
    for d in rep["dropped_responses"]:
        committed_by_fan[d["fan"]] += 1
    gave_up_but_committed = sum(1 for f in gave_up if committed_by_fan[f["id"]] > 0)
    delays = {}
    for _, c in calls:
        if "backoff_s" in c:
            delays.setdefault(f"after_attempt_{c['attempt']}", []).append(c["backoff_s"])
    delays = {k: {"n": len(v), "min_s": min(v), "max_s": max(v)} for k, v in sorted(delays.items())}
    return {
        "pct": int(path.stem.split("-")[1]), "file": path.name, "fans": len(fans),
        "http_calls": len(calls),
        "calls_by_outcome": dict(Counter(str(c["outcome"]) for _, c in calls)),
        "client_timeouts": len(timeouts),
        "timeouts_that_had_committed": committed_timeouts,
        "client_non_201_calls": len(non_201),
        "fans_confirmed": sum(f["outcome"] == "confirmed" for f in fans),
        "fans_gave_up": len(gave_up),
        "gave_up_but_server_committed": gave_up_but_committed,
        "responses_dropped_server": rep["responses_dropped_after_commit"],
        "fans_with_duplicate_holds": ev["fans_with_duplicate_holds"],
        "fans_with_duplicate_orders": ev["fans_with_duplicate_orders"],
        "retried_duplicates": ev["retried_duplicates"],
        "orders_confirmed": ev["orders_confirmed"],
        "seats_unavailable_on_server": ev["seats_unavailable"],
        "duplicate_sales_same_seat": ev["duplicate_sales"],
        "capacity": ev["capacity"],
        "backoff_delays_s": delays,
    }


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(json.dumps(summarize(Path(p)), indent=1))

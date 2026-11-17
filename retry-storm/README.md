# retry-storm: The Retry Storm

100 fans each buy one ticket for the Velvet Static Tour (event 3, 1000 seats) with a standard
"retry on timeout, exponential backoff" client and no idempotency key. The server toggle
`DROP_RESPONSE_AFTER_COMMIT_PCT` makes a share of successful writes commit but never answer.

## Versions (2026-11-16)
Python 3.12.6 (ticket-rush `demo-api/.venv`), httpx 0.28.1, FastAPI 0.143.0, uvicorn 0.54.0,
pydantic 2.14.1. ticket-rush on top of video 6 plus the response-drop toggle
(`app/faults.py`, config, admin report).

## Run
```bash
# needs ticket-rush at TICKET_RUSH_DIR (default: the parent of this folder) with its venv installed
python run_demo.py 0 10 20 40          # starts the API for each %, runs the fans, stops it
python summarize.py results/pct-20.json
python timeline.py results/pct-20.json            # a fan whose reservation reply was lost
python timeline.py results/pct-20.json fan-000    # a fan whose payment reply was lost
```
`run_demo.py` uses the ticket-rush venv python, so no extra install is needed (httpx is in
`requirements.txt` if you use your own).

## Client policy
Up to 3 attempts per call, retry on timeout only, client timeout 1.0 s, wait
0.5 s x 2^(attempt-1) plus 0 to 0.1 s seeded jitter. If a reservation answers 409
(seat not available) the fan tries their next seat. No idempotency key (that comes in the next video).

## What is seeded and what is not
Seeded and repeatable: which writes are dropped (`DROP_SEED=42`, keyed on fan, path and that fan's call count,
so concurrency does not change it), each fan's seats, backoff jitter. Verified: two runs at 20% dropped
the identical set of (fan, path) calls. Not seeded: reservation and order ids, wall-clock timestamps,
exact millisecond latencies (the client timeout is 1.0 s but the event loop is busy with 100 fans, so
timeouts report about 1.0 to 1.4 s).

`results/` holds the raw output of the 20% run shown in the video (the 0, 10 and 40% runs are not included; rerun to regenerate them). No secrets, all fictional.

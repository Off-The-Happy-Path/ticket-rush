# demo-api

A concert-ticketing API built for load-testing demos. Tickets go on sale, thousands of fans hit Buy at once.

FastAPI, in-memory storage, one process. Data resets on every restart.

## Run it

Python 3.12 or newer.

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows
source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --log-level warning
```

Open http://localhost:8000/docs for the interactive API docs.

`--log-level warning` turns off the per-request log. Under load, printing every request costs real CPU, especially in a Windows console, so leave it off when you measure. All numbers in the videos were measured this way.

## Settings

Set these as environment variables before starting the server.

| Variable | Default | What it does |
| --- | --- | --- |
| `OVERSELL_BUG` | `false` | `true` removes the seat lock, so two fans can buy the same seat |
| `ADMIN_ENABLED` | `false` | `true` adds `/admin/reset`, `/admin/report` and `/admin/freeze` (hidden from `/docs`) |
| `HOLD_SECONDS` | `300` | How long a reservation holds a seat |
| `DB_LATENCY_MS` | `50` | Simulated database round trip |
| `PAYMENT_LATENCY_MS` | `200` | Simulated payment call |
| `DROP_RESPONSE_AFTER_COMMIT_PCT` | `0` | 0-100. For this % of successful `POST /reservations` and `POST /orders`, the write commits but the response is never sent (the client times out). Needs `ADMIN_ENABLED=true` to see the effect in `/admin/report` |
| `DROP_SEED` | `0` | Makes the dropped requests reproducible |
| `DROP_HOLD_SECONDS` | `5` | How long a dropped response is held before the server gives up |

PowerShell:

```powershell
$env:OVERSELL_BUG="true"; $env:ADMIN_ENABLED="true"; uvicorn app.main:app --port 8000 --log-level warning
```

macOS / Linux:

```bash
OVERSELL_BUG=true ADMIN_ENABLED=true uvicorn app.main:app --port 8000 --log-level warning
```

## Endpoints

| Endpoint | What it does |
| --- | --- |
| `GET /events` | Upcoming concerts with seats left |
| `GET /events/{id}/seats?status=available` | Seat map |
| `POST /reservations` | Hold a seat |
| `POST /orders` | Pay for a held seat |
| `GET /orders/{id}` | Order status |
| `GET /health` | Shows whether the bug and admin endpoints are on |
| `POST /admin/reset` | Fresh data. Body `{"sale_opens_in_seconds": 60}` delays the sale |
| `GET /admin/report` | Orders vs seats, and every seat sold more than once |
| `POST /admin/freeze?seconds=3` | Blocks the whole API for that long, like a blocking call in async code |

With the drop toggle on, `/admin/report` also shows `retried_duplicates` (extra holds and orders by a fan who already had one for the event), `fans_with_duplicate_holds`, `seats_unavailable` and every dropped response.

The report always adds up: `orders_confirmed = unique_seats_sold + duplicate_sales`. A seat sold three times counts as one oversold seat and two duplicate sales.

Errors always look like `{"error": "seat_not_available", "message": "..."}`.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

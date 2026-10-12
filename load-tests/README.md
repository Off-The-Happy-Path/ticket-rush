# load-tests

Locust load tests for the ticket-rush API.

| File | Scenario | Used in |
| --- | --- | --- |
| `locustfile.py` | `Fan`: a normal mix. Browse events 5×, check seats 3×, reserve 1× | Video 1 |
| `ticket_rush.py` | `RushFan`: the sale opens and everyone grabs the best seats of the 120-seat show. Fails the run if any seat is sold twice | The 10:00 sale video |

## Setup

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows
source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

## Normal traffic (video 1)

Start the API (see [`../demo-api`](../demo-api/README.md)), then:

```bash
locust -f locustfile.py --host http://127.0.0.1:8000
```

Open http://localhost:8089. More users than one process can handle? Add workers:

```bash
locust -f locustfile.py --master --host http://127.0.0.1:8000
locust -f locustfile.py --worker      # run in several more terminals
```

Use `127.0.0.1`, not `localhost`. On Windows, `localhost` tries IPv6 first, and every new connection then waits about 2 seconds before falling back. That fake latency shows up in your p95.

A `409 seat_not_available` counts as success: during a sale, "someone else got it" is a normal answer.

## The ticket rush

The API must run with `ADMIN_ENABLED=true`. The test resets the data, opens the sale 15 seconds after it starts, and checks `/admin/report` when it stops.

```bash
locust -f ticket_rush.py --headless -u 500 -r 100 --run-time 40s --host http://127.0.0.1:8000
```

- `OVERSELL_BUG=false`: exactly 120 tickets for 120 seats, exit code 0.
- `OVERSELL_BUG=true`: more tickets than seats, `OVERSOLD` in the log, exit code 1.

## A note on these numbers

For the demo, Locust and the API run on the same machine. In real tests, keep the load generator on separate machines: they compete for CPU, and both sets of numbers get worse.

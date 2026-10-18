# api-tests-java

Functional tests for the ticket-rush API: Java, TestNG and REST Assured.

You only need Java 17 or newer. The Maven Wrapper (`mvnw`) downloads Maven on the first run and checks it against a pinned SHA-256.

## Run

1. Start the API with admin endpoints on (see [`../demo-api`](../demo-api/README.md)):

   ```bash
   ADMIN_ENABLED=true uvicorn app.main:app --port 8000
   ```

2. Run the tests:

   ```bash
   ./mvnw test          # macOS / Linux / Git Bash
   mvnw.cmd test        # Windows cmd / PowerShell
   ```

   Against another address: `./mvnw test -Dapi.baseUri=http://localhost:9000`

Every test starts from fresh data (`POST /admin/reset`), so the order doesn't matter.

## What these tests don't catch

Every test except `ConcurrencyTest` passes even with `OVERSELL_BUG=true`. They send one request at a time, and the bug only shows up when many fans buy at once.

`onlyOneFanGetsTheSeat` (in `ConcurrencyTest`) sends 50 fans after the same seat at the same moment and expects exactly one winner. A race doesn't show up on every attempt, so it runs 5 times (TestNG counts each one, so the report says 20 tests). With the bug on, the race usually lets 2 to 15 fans get the seat.

`ticketsSoldNeverExceedSeats` (also in `ConcurrencyTest`) checks an invariant instead of a response: 160 fans buy the 20 front-row seats at once, then the number of tickets sold (`/admin/report`) must not be more than the number of seats marked sold. With the bug on it fails with something like "28 tickets sold for 20 seats". For a whole sale, see [`../load-tests`](../load-tests).

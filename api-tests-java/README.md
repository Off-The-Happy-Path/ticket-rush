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

All tests pass even with `OVERSELL_BUG=true`. They send one request at a time, and the bug only shows up when many fans buy at once. That's what [`../load-tests`](../load-tests) is for.

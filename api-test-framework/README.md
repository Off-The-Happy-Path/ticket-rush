# api-test-framework: an API test framework built around what goes wrong

Java 17 target (`maven.compiler.release`), REST Assured 5.5.7, TestNG 7.12.0, Jackson 2.22.2,
maven-surefire 3.5.6, Maven 3.9.16 via the wrapper. Runs against ticket-rush (concert-ticketing demo API).

## Start two ticket-rush instances (local and ci)
```bash
./start-servers.sh   # :8000 HOLD_SECONDS=2, :8001 HOLD_SECONDS=4, OVERSELL_BUG=false, ADMIN_ENABLED=true
```
Needs the `demo-api` venv with its requirements installed. `OVERSELL_BUG=true ./start-servers.sh` gives the red run.

## Run
```bash
./mvnw -Denv=local test                            # full suite, 17 tests, config from src/test/resources/env/local.properties
./mvnw -Denv=ci test                               # same suite, ci config (port 8001, hold 4 s, 30 threads)
./mvnw -Denv=ci -Dthreads=10 test                  # any key can be overridden: -D<key> or TR_<KEY> env var
./mvnw -Denv=local -Dsuite=suites/smoke.xml test   # smoke | concurrency | full
```
Startup prints one line: `[config] env=... base.url=... hold.seconds=... timeout.ms=... threads=...`.
TestNG report: `target/surefire-reports/index.html` (also `emailable-report.html`).

## Flake demo (N = 20, about 40 s each)
```bash
./mvnw -Denv=local -Dsuite=suites/flake-fixed-sleep.xml -Dmaven.test.failure.ignore=true test                    # v1: Thread.sleep(1800)
./mvnw -Denv=local -Dv1.sleep.ms=1500 -Dsuite=suites/flake-fixed-sleep.xml -Dmaven.test.failure.ignore=true test  # tighter sleep
./mvnw -Denv=local -Dsuite=suites/flake-polling.xml -Dmaven.test.failure.ignore=true test                        # framework: polling helper
```
`-Dsuite=suites/v1.xml` runs the five v1 "copy-paste" tests (hard-coded URL, ignores `-Denv`).

## Layout
`config` (env loader) / `client` (ApiClient, Wait) / `data` (SeatAllocator, Fans) / `assertions` (Invariants) /
`tests/{smoke,api,concurrency,flake}` / `v1` (the deliberately naive version, kept only for the comparison).

## What is random
Nothing is seeded. Timing is real: the demo API's clock truncates to whole seconds, so a "2 s" hold really lasts
between 1 and 2 s. That is what makes a fixed sleep flaky. Flake counts depend on the sleep value and on where in
the second each request lands. Flake counts vary from run to run; they are not reproducible to the digit.

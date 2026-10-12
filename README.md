# ticket-rush

Demo code for a YouTube channel about API and performance testing.

The system under test is a concert-ticketing API: tickets go on sale at 10:00 and thousands of fans hit Buy in the same second. It has a switchable overselling bug, so you can watch a load test catch two fans buying the same seat.

| Folder | What's inside |
| --- | --- |
| [`demo-api/`](demo-api/) | The ticketing API (Python, FastAPI) |
| [`api-tests-java/`](api-tests-java/) | Functional API tests (Java, TestNG, REST Assured) |
| [`load-tests/`](load-tests/) | Locust load tests: normal traffic and the ticket rush |

Each video links to a git tag (`v01-locust`, `v02-...`) with the exact code shown on screen.

Everything here is fictional: the concerts, venues and traffic numbers.

# ticket-rush

Demo code for **[Off the Happy Path](https://www.youtube.com/channel/UCZ0jt4_8YMm68yZ4iPDJb3g)**, a YouTube channel about API and performance testing.

The system under test is a concert-ticketing API: tickets go on sale at 10:00 and thousands of fans hit Buy in the same second. It has a switchable overselling bug, so you can watch a load test catch two fans buying the same seat.

| Folder | What's inside |
| --- | --- |
| [`demo-api/`](demo-api/) | The ticketing API (Python, FastAPI) |
| [`api-tests-java/`](api-tests-java/) | Functional API tests (Java, TestNG, REST Assured) |
| [`api-tests-postman/`](api-tests-postman/) | The video 3 test as a Postman collection, run with Newman |
| [`api-tests-playwright/`](api-tests-playwright/) | The video 3 test with Playwright (TypeScript) |
| [`load-tests/`](load-tests/) | Locust load tests: normal traffic and the ticket rush |

```bash
git clone https://github.com/Off-The-Happy-Path/ticket-rush.git
```

Each video links to a git tag (`v01-locust`, `v02-...`) with the exact code shown on screen:

| Video | Code |
| --- | --- |
| Load Testing an API with Locust: Finding the Breaking Point | [`v01-locust`](https://github.com/Off-The-Happy-Path/ticket-rush/tree/v01-locust) |
| Why Your API Tests Pass but Production Still Breaks | [`v02-production-gaps`](https://github.com/Off-The-Happy-Path/ticket-rush/tree/v02-production-gaps) |
| REST Assured vs Postman vs Playwright: Which to Learn in 2027 | [`v03-three-tools`](https://github.com/Off-The-Happy-Path/ticket-rush/tree/v03-three-tools) |

Everything here is fictional: the concerts, venues and traffic numbers.

MIT licensed, see [LICENSE](LICENSE).

# api-tests-playwright

The video 3 test with Playwright's `request` fixture: fan 1 reserves seat B-7, B-7 leaves the available list, fan 2 gets a 409.

You need the API running with admin endpoints on (see [`../demo-api`](../demo-api/README.md)); each test resets the demo data first. Node 18 or newer. API tests don't open a browser, so there's no browser download:

```bash
npm install
npm test
```

Against another address: `API_BASE_URL=http://localhost:9000 npm test`

# api-tests-postman

The video 3 test as a Postman collection: fan 1 reserves seat B-7, B-7 leaves the available list, fan 2 gets a 409.

You need the API running with admin endpoints on (see [`../demo-api`](../demo-api/README.md)). The first request resets the demo data before it runs.

## In the Postman app

Import `ticket-rush.postman_collection.json` (File → Import), then run it with the Collection Runner. The test scripts are under each request's Scripts → After response.

## From the command line (Newman)

Newman runs the same file, needs no Postman account, and fits in CI. Node 18 or newer:

```bash
npm install
npm test
```

Against another address: `npx newman run ticket-rush.postman_collection.json --env-var baseUrl=http://localhost:9000`

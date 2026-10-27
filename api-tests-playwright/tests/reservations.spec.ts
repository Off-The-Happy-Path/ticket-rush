import { test, expect } from '@playwright/test';

// Every test starts from fresh data, like the Java tests (needs ADMIN_ENABLED=true)
test.beforeEach(async ({ request }) => {
  await request.post('/admin/reset', { data: {} });
});

test('second fan cannot take a held seat', async ({ request }) => {
  const first = await request.post('/reservations', {
    data: { event_id: 2, seat_id: 'B-7', customer_id: 'fan-1' },
  });
  expect(first.status()).toBe(201);

  const seats = await request.get('/events/2/seats', { params: { status: 'available' } });
  const ids = (await seats.json()).seats.map((s) => s.seat_id);
  expect(ids).not.toContain('B-7');

  const second = await request.post('/reservations', {
    data: { event_id: 2, seat_id: 'B-7', customer_id: 'fan-2' },
  });
  expect(second.status()).toBe(409);
});

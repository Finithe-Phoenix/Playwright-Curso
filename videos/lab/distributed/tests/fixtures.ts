import { randomUUID } from 'node:crypto';
import { test as base, expect } from '@playwright/test';

export type Lab = { fixtureId: string; username: string; password: string; sourceAccountId: string; beneficiaryId: string };
const runId = process.env.RUN_ID || `course-${randomUUID()}`;

export const test = base.extend<{ lab: Lab }>({
  lab: async ({ playwright, page, baseURL }, use, testInfo) => {
    const key = process.env.TEST_HOOK_KEY;
    if (!key) throw new Error('Set TEST_HOOK_KEY in this terminal.');
    const admin = await playwright.request.newContext({ baseURL, extraHTTPHeaders: { 'X-Test-Hook-Key': key } });
    let lab: Lab | undefined;
    try {
      const health = await admin.get('/health');
      expect(health.status()).toBe(200);
      expect(await health.json()).toMatchObject({ status: 'ok', environment: 'test', contractVersion: '1' });
      const created = await admin.post('/__test/fixtures', { data: {
        runId, caseId: testInfo.title, currency: 'MXN', balanceMinor: 100000,
      } });
      expect(created.status()).toBe(201);
      lab = await created.json();
      const login = await page.request.post('/api/session', { data: { username: lab!.username, password: lab!.password } });
      expect(login.status()).toBe(200);
      await use(lab!);
    } finally {
      if (lab) {
        // Attach observable business state before teardown, with no credentials in this JSON.
        try {
          const account = await page.request.get(`/api/accounts/${lab.sourceAccountId}`);
          const transfers = await page.request.get('/api/transfers', { params: { sourceAccountId: lab.sourceAccountId } });
          await testInfo.attach('business-state', { body: JSON.stringify({ fixtureId: lab.fixtureId,
            account: await account.json(), transfers: await transfers.json() }, null, 2), contentType: 'application/json' });
        } finally {
          const cleanup = await admin.delete(`/__test/fixtures/${lab.fixtureId}`);
          expect(cleanup.status(), `Cleanup failed for fixture ${lab.fixtureId}`).toBe(204);
          const revoked = await page.request.get(`/api/accounts/${lab.sourceAccountId}`);
          expect(revoked.status(), 'Fixture cleanup must revoke its sessions').toBe(401);
        }
      }
      await admin.dispose();
    }
  },
});
export { expect };

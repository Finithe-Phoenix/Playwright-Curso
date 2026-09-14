import { test, expect } from '@playwright/test';
import { randomUUID } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import path from 'node:path';

// Production capture only: holds make actions readable on film, never synchronize assertions.
for (const scenario of ['success', 'insufficient', 'unavailable'] as const) {
  test(`record-${scenario}`, async ({ page }, info) => {
    const adminHeaders = { 'X-Test-Hook-Key': process.env.TEST_HOOK_KEY || 'classroom-demo-only' };
    const created = await page.request.post('/__test/fixtures', { headers: adminHeaders,
      data: { runId: randomUUID(), caseId: `motion-${scenario}`, balanceMinor: 100000, currency: 'MXN' } });
    expect(created.status()).toBe(201);
    const fixture = await created.json();
    const started = Date.now();
    const events: { time: number; action: string; code: string }[] = [];
    const mark = (action: string, code: string) => events.push({ time: (Date.now() - started) / 1000, action, code });
    const hold = () => new Promise(resolve => setTimeout(resolve, 2200));
    try {
      expect((await page.request.post('/api/session', { data: { username: fixture.username, password: fixture.password } })).status()).toBe(200);
      mark('Open the transfer workspace', "await page.goto('/transfers');");
      await page.goto('/transfers');
      await expect(page.getByTestId('account-balance')).toHaveText('MXN 1000.00');
      await hold();
      mark('Select the owned source account', "await page.getByLabel('Source account').selectOption(lab.sourceAccountId);");
      await page.getByLabel('Source account', { exact: true }).selectOption(fixture.sourceAccountId);
      await page.getByLabel('Source account', { exact: true }).focus();
      await hold();
      mark('Select the isolated beneficiary', "await page.getByLabel('Beneficiary').selectOption(lab.beneficiaryId);");
      await page.getByLabel('Beneficiary', { exact: true }).selectOption(fixture.beneficiaryId);
      await page.getByLabel('Beneficiary', { exact: true }).focus();
      await hold();
      if (scenario === 'unavailable') {
        await page.route('**/api/transfers', route => route.request().method() === 'POST'
          ? route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ code: 'SERVICE_UNAVAILABLE', message: 'Service temporarily unavailable' }) })
          : route.continue());
      }
      mark('Type the amount', `await page.getByLabel('Amount (MXN)').fill('${scenario === 'insufficient' ? '1100.00' : '100.00'}');`);
      await page.getByLabel('Amount (MXN)', { exact: true }).pressSequentially(scenario === 'insufficient' ? '1100.00' : '100.00', { delay: 240 });
      await hold();
      mark('Submit the customer action', "await page.getByRole('button', { name: 'Transfer', exact: true }).click();");
      const response = page.waitForResponse(r => r.request().method() === 'POST' && new URL(r.url()).pathname === '/api/transfers');
      await page.getByRole('button', { name: 'Transfer', exact: true }).click();
      const posted = await response;
      expect(posted.status()).toBe(scenario === 'success' ? 201 : scenario === 'insufficient' ? 422 : 503);
      const result = await posted.json();
      await expect(page.getByRole(scenario === 'success' ? 'status' : 'alert')).toHaveText(scenario === 'success' ? 'Transfer completed' : scenario === 'insufficient' ? 'Insufficient funds' : 'Service temporarily unavailable');
      await expect(page.getByTestId('account-balance')).toHaveText(scenario === 'success' ? 'MXN 900.00' : 'MXN 1000.00');
      mark('Assert the visible business result', `await expect(page.getByTestId('account-balance')).toHaveText('MXN ${scenario === 'success' ? '900' : '1000'}.00');`);
      await hold();
      const account = await (await page.request.get(`/api/accounts/${fixture.sourceAccountId}`)).json();
      const canonical = await (await page.request.get('/api/transfers', { params: { sourceAccountId: fixture.sourceAccountId } })).json();
      expect(account.balanceMinor).toBe(scenario === 'success' ? 90000 : 100000);
      expect(canonical.total).toBe(scenario === 'success' ? 1 : 0);
      if (scenario === 'success') expect(canonical.items[0].id).toBe(result.id);
      if (scenario === 'success' && process.env.TNZ_PYTHON) {
        const terminal = JSON.parse(execFileSync(process.env.TNZ_PYTHON, [path.resolve('../mainframe/adapter.py'), 'lookup', result.id,
          '--port', process.env.TNZ_PORT || '2423', '--snapshot', info.outputPath('terminal.txt')], { timeout: 12000, encoding: 'utf8', windowsHide: true }));
        expect(terminal.reference).toBe(result.id);
        expect(terminal.amountMinor).toBe(10000);
        expect(terminal.balanceMinor).toBe(account.balanceMinor);
        await info.attach('terminal-result', { body: JSON.stringify(terminal, null, 2), contentType: 'application/json' });
      }
      mark('Verify canonical API state', `expect(account.balanceMinor).toBe(${account.balanceMinor});\nexpect(transfers.total).toBe(${canonical.total});`);
      await page.screenshot({ path: info.outputPath('final.png') });
      await hold();
      await info.attach('capture-events', { body: JSON.stringify({ scenario, events, result, balanceMinor: account.balanceMinor,
        transferCount: canonical.total, timingBasis: 'wall clock since test setup; video includes short browser startup lead-in' }, null, 2), contentType: 'application/json' });
    } finally {
      expect((await page.request.delete(`/__test/fixtures/${fixture.fixtureId}`, { headers: adminHeaders })).status()).toBe(204);
    }
  });
}

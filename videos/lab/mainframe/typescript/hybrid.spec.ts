import { test, expect } from '../../distributed/node_modules/@playwright/test';
import { execFile } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { promisify } from 'node:util';

const runFile = promisify(execFile);
const mainframe = path.resolve(__dirname, '..');
const evidence = path.join(mainframe, 'evidence');

test('browser transfer matches the simulated 3270 terminal', async ({ page, context }) => {
  const hookKey = process.env.TEST_HOOK_KEY;
  expect(hookKey, 'Set TEST_HOOK_KEY to the running local gateway key').toBeTruthy();
  const headers = { 'X-Test-Hook-Key': hookKey! };
  const created = await context.request.post('/__test/fixtures', { headers, data: {
    runId: `typescript-hybrid-${randomUUID()}`, caseId: 'HYBRID-TS-01', currency: 'MXN', balanceMinor: 100000,
  }});
  expect(created.status()).toBe(201);
  const fixture = await created.json();
  try {
    const login = await context.request.post('/api/session', { data: {
      username: fixture.username, password: fixture.password,
    }});
    expect(login.status()).toBe(200);
    await page.goto('/transfers');
    await page.getByLabel('Cuenta origen', { exact: true }).selectOption(fixture.sourceAccountId);
    await page.getByLabel('Beneficiario', { exact: true }).selectOption(fixture.beneficiaryId);
    await page.getByLabel('Importe (MXN)', { exact: true }).fill('100.00');
    await page.getByRole('button', { name: 'Transferir', exact: true }).click();
    await expect(page.getByRole('status')).toHaveText('Transferencia realizada');
    await expect(page.getByTestId('account-balance')).toHaveText('MXN 900.00');
    const response = await context.request.get('/api/transfers', { params: { sourceAccountId: fixture.sourceAccountId } });
    expect(response.status()).toBe(200);
    const transfers = await response.json();
    expect(transfers.total).toBe(1);
    const reference = transfers.items[0].id;
    const python = process.env.TNZ_PYTHON || path.join(mainframe,
      process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python');
    await mkdir(evidence, { recursive: true });
    // Exact arguments; no shell. execFile rejects a nonzero exit or a 12-second timeout.
    const { stdout } = await runFile(python, [path.join(mainframe, 'adapter.py'), 'lookup', reference,
      '--timeout', '8', '--snapshot', path.join(evidence, 'hybrid-typescript-terminal.txt')],
      { timeout: 12000, windowsHide: true });
    const terminal = JSON.parse(stdout);
    expect(terminal).toEqual({ reference, status: 'COMPLETED', simulated: true,
      amountMinor: 10000, currency: 'MXN', sourceAccountId: fixture.sourceAccountId, balanceMinor: 90000 });
    await writeFile(path.join(evidence, 'hybrid-typescript-result.json'), JSON.stringify(terminal, null, 2));
    await page.screenshot({ path: path.join(evidence, 'hybrid-typescript-browser.png'), fullPage: true });
  } finally {
    const deleted = await context.request.delete(`/__test/fixtures/${fixture.fixtureId}`, { headers });
    expect(deleted.status(), 'Fixture cleanup').toBe(204);
  }
});

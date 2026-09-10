import { randomUUID } from 'node:crypto';
import type { Page } from '@playwright/test';
import { test, expect, type Lab } from './fixtures';

async function fillTransfer(page: Page, lab: Lab, amount = '100.00') {
  await page.goto('/transfers');
  await page.getByLabel('Cuenta origen', { exact: true }).selectOption(lab.sourceAccountId);
  await page.getByLabel('Beneficiario', { exact: true }).selectOption(lab.beneficiaryId);
  await page.getByLabel('Importe (MXN)', { exact: true }).fill(amount);
}
async function state(page: Page, lab: Lab, balance: number, count: number) {
  const account = await page.request.get(`/api/accounts/${lab.sourceAccountId}`);
  expect(account.status()).toBe(200);
  expect((await account.json()).balanceMinor).toBe(balance);
  const response = await page.request.get('/api/transfers', { params: { sourceAccountId: lab.sourceAccountId } });
  expect(response.status()).toBe(200);
  const ledger = await response.json();
  expect(ledger.total).toBe(count);
  expect(ledger.items).toHaveLength(count);
  return ledger.items;
}
const transferBody = (lab: Lab, amountMinor = 10000) => ({ sourceAccountId: lab.sourceAccountId,
  beneficiaryId: lab.beneficiaryId, currency: 'MXN', amountMinor });

test('TR-01 | UI transfer commits exactly one debit and record', async ({ page, lab }) => {
  await fillTransfer(page, lab);
  await page.getByRole('button', { name: 'Transferir', exact: true }).click();
  await expect(page.getByRole('status')).toHaveText('Transferencia realizada');
  await expect(page.getByTestId('account-balance')).toHaveText('MXN 900.00');
  const items = await state(page, lab, 90000, 1);
  expect(items[0]).toMatchObject({ ...transferBody(lab), status: 'COMPLETED' });
  await page.screenshot({ path: test.info().outputPath('ui-success.png'), fullPage: true });
});

test('TR-02 | Insufficient funds leaves balance and ledger unchanged', async ({ page, lab }) => {
  await fillTransfer(page, lab, '1100.00');
  const pending = page.waitForResponse(response => new URL(response.url()).pathname === '/api/transfers'
    && response.request().method() === 'POST');
  await page.getByRole('button', { name: 'Transferir', exact: true }).click();
  const response = await pending;
  expect(response.status()).toBe(422);
  expect((await response.json()).code).toBe('INSUFFICIENT_FUNDS');
  await expect(page.getByRole('alert')).toHaveText('Saldo insuficiente');
  await state(page, lab, 100000, 0);
});

test('TR-03 | Sequential retry uses same key, body and transfer id', async ({ page, lab }) => {
  const options = { headers: { 'Idempotency-Key': randomUUID() }, data: transferBody(lab) };
  const first = await page.request.post('/api/transfers', options);
  const second = await page.request.post('/api/transfers', options);
  expect(first.status()).toBe(201);
  expect(second.status()).toBe(200);
  const original = await first.json();
  expect(await second.json()).toEqual(original);
  const items = await state(page, lab, 90000, 1);
  expect(items[0].id).toBe(original.id);
  await page.goto('/transfers');
  await expect(page.getByTestId('account-balance')).toHaveText('MXN 900.00');
});

for (const amount of [0, -1, 0.5]) {
  test(`TR-04 | API rejects invalid minor amount ${amount}`, async ({ page, lab }) => {
    const response = await page.request.post('/api/transfers', {
      headers: { 'Idempotency-Key': randomUUID() }, data: transferBody(lab, amount),
    });
    expect(response.status()).toBe(422);
    expect((await response.json()).code).toBe('INVALID_AMOUNT');
    await state(page, lab, 100000, 0);
  });
}

test('TR-05 | Mocked503 verifies UI recovery without backend effects', async ({ page, lab }) => {
  await page.route('**/api/transfers', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    await route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({
      code: 'SERVICE_UNAVAILABLE', message: 'Servicio temporalmente no disponible',
    }) });
  });
  try {
    await fillTransfer(page, lab);
    await page.getByRole('button', { name: 'Transferir', exact: true }).click();
    await expect(page.getByRole('alert')).toHaveText('Servicio temporalmente no disponible');
    await expect(page.getByRole('button', { name: 'Transferir', exact: true })).toBeEnabled();
    await state(page, lab, 100000, 0);
  } finally { await page.unroute('**/api/transfers'); }
});

test('TR-06 | Exact reference reaches the independent ledger within5seconds', async ({ page, lab }) => {
  const posted = await page.request.post('/api/transfers', {
    headers: { 'Idempotency-Key': randomUUID() }, data: transferBody(lab),
  });
  expect(posted.status()).toBe(201);
  const transfer = await posted.json();
  // Bounded business-state polling is separate from Playwright locator auto-waiting.
  await expect.poll(async () => {
    const response = await page.request.get('/api/ledger/transfers', { params: { sourceAccountId: lab.sourceAccountId } });
    expect(response.status()).toBe(200);
    return (await response.json()).items.find((item: {id: string}) => item.id === transfer.id);
  }, { timeout: 5000, intervals: [100, 250, 500], message: `Ledger must project transfer ${transfer.id}` })
    .toEqual(transfer);
  const lookup = await page.request.get('/__test/lookup', { params: { reference: transfer.id } });
  expect(lookup.status()).toBe(200);
  expect(await lookup.json()).toEqual({ reference: transfer.id, status: 'COMPLETED', amountMinor: 10000,
    currency: 'MXN', sourceAccountId: lab.sourceAccountId, balanceMinor: 90000 });
});

test('TR-07 | Reusing an idempotency key with different amount conflicts', async ({ page, lab }) => {
  const headers = { 'Idempotency-Key': randomUUID() };
  expect((await page.request.post('/api/transfers', { headers, data: transferBody(lab) })).status()).toBe(201);
  const conflict = await page.request.post('/api/transfers', { headers, data: transferBody(lab, 20000) });
  expect(conflict.status()).toBe(409);
  expect((await conflict.json()).code).toBe('IDEMPOTENCY_CONFLICT');
  await state(page, lab, 90000, 1);
});

test('TR-08 | Missing session and cross-fixture account access are rejected', async ({ page, lab, playwright, baseURL }) => {
  const anonymous = await playwright.request.newContext({ baseURL });
  try { expect((await anonymous.get(`/api/accounts/${lab.sourceAccountId}`)).status()).toBe(401); }
  finally { await anonymous.dispose(); }
  const admin = await playwright.request.newContext({ baseURL,
    extraHTTPHeaders: { 'X-Test-Hook-Key': process.env.TEST_HOOK_KEY! } });
  let other: Lab | undefined;
  try {
    const seeded = await admin.post('/__test/fixtures', { data: {
      runId: `authorization-${randomUUID()}`, caseId: 'TR-08-other', currency: 'MXN', balanceMinor: 100000,
    } });
    expect(seeded.status()).toBe(201);
    other = await seeded.json();
    expect((await page.request.get(`/api/accounts/${other!.sourceAccountId}`)).status()).toBe(403);
    const forbidden = await page.request.post('/api/transfers', {
      headers: { 'Idempotency-Key': randomUUID() }, data: { ...transferBody(lab), beneficiaryId: other!.beneficiaryId },
    });
    expect(forbidden.status()).toBe(403);
  } finally {
    try { if (other) expect((await admin.delete(`/__test/fixtures/${other.fixtureId}`)).status()).toBe(204); }
    finally { await admin.dispose(); }
  }
  await state(page, lab, 100000, 0);
});

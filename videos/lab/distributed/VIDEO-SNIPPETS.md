# Source-backed snippets for the English video lessons

These snippets are extracted from the executed TypeScript suite. Full setup and teardown live in `tests/fixtures.ts`; they are needed before using the test bodies below.

## 1. One user action, two independent assertions

Source: `tests/regression.spec.ts`, TR-01 and its `state` helper.

```typescript
await page.getByLabel('Importe (MXN)', { exact: true }).fill('100.00');
await page.getByRole('button', { name: 'Transferir', exact: true }).click();
await expect(page.getByRole('status')).toHaveText('Transferencia realizada');
await expect(page.getByTestId('account-balance')).toHaveText('MXN 900.00');

const account = await page.request.get(`/api/accounts/${lab.sourceAccountId}`);
expect(account.status()).toBe(200);
expect((await account.json()).balanceMinor).toBe(90000);
```

Narration: “First, use the accessible label to enter one hundred pesos. Then click Transfer. Playwright waits for the visible confirmation and the new balance. Finally, query the real account API using the page's authenticated request client. The interface and the authoritative balance must agree. The full test also verifies exactly one matching transfer record.”

## 2. Idempotency is one intention replayed

Source: `tests/regression.spec.ts`, TR-03.

```typescript
const options = {
  headers: { 'Idempotency-Key': randomUUID() },
  data: transferBody(lab),
};
const first = await page.request.post('/api/transfers', options);
const second = await page.request.post('/api/transfers', options);
expect(first.status()).toBe(201);
expect(second.status()).toBe(200);
expect(await second.json()).toEqual(await first.json());
await state(page, lab, 90000, 1);
```

Narration: “Create the key once, outside both requests. Send exactly the same body twice. The first request creates the transfer. The second must return the same transfer identifier and result. Verify the balance and the number of records as well. Two independent clicks with different keys do not test this property. This example covers sequential retries; concurrent retries require a separate scenario.”

## 3. Poll the business event, with a deadline

Source: `tests/regression.spec.ts`, TR-06. `transfer` is the object returned by the successful real transfer request.

```typescript
await expect.poll(async () => {
  const response = await page.request.get('/api/ledger/transfers', {
    params: { sourceAccountId: lab.sourceAccountId },
  });
  expect(response.status()).toBe(200);
  return (await response.json()).items.find(
    (item: { id: string }) => item.id === transfer.id,
  );
}, { timeout: 5000, intervals: [100, 250, 500] }).toEqual(transfer);
```

Narration: “The accounts service already committed the transfer, but the independent ledger projection may still be catching up. Query the projection by the isolated source account and search for the exact returned transfer identifier. Retry the read within a five-second deadline. A missing event fails the test. A fixed sleep cannot express this business condition, and locator auto-waiting does not observe another service's state.”

## Genuine failure checkpoint

`evidence/defect/results.json` records the controlled TR-03 failure. Its attached business state shows 80000 minor units and two records after the replay. Compare it with the healthy run's 90000 and one record. The correct response is to fix idempotency handling, preserving the business expectation.

## Media paths

- Happy UI: `evidence/test-results/regression-TR-01-UI-transf-6b8b3-xactly-one-debit-and-record-chromium/ui-success.png`
- Short browser recording: same directory, `video.webm`
- Rejection screenshot: `evidence/test-results/regression-TR-02-Insuffici-7170f-alance-and-ledger-unchanged-chromium/test-finished-1.png`
- Defect trace: `evidence/defect/test-results/regression-TR-03-Sequentia-22c57-me-key-body-and-transfer-id-chromium/trace.zip`

The runner videos are brief execution evidence. They are not the narrated lesson videos; the parent video production pipeline assembles those separately.

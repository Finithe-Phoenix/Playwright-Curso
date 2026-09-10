import { accountsURL, call, fail, json, listen, requireInternal } from './common.mjs';

const records = new Map();
let cursor = 0;
let syncTask;
function synchronize() {
  if (syncTask) return syncTask;
  syncTask = (async () => {
  try {
    const response = await call(`${accountsURL}/outbox?after=${cursor}`);
    if (response.status !== 200) return;
    for (const event of response.data.events) {
      if (event.type === 'transfer.completed') records.set(event.data.transfer.id, event.data);
      if (event.type === 'fixture.deleted') {
        for (const [id, entry] of records) if (entry.fixtureId === event.data.fixtureId) records.delete(id);
      }
      cursor = event.sequence;
    }
  } catch { /* A future poll retries; callers use a bounded assertion, not a success assumption. */ }
  })().finally(() => { syncTask = undefined; });
  return syncTask;
}
setInterval(synchronize, Number(process.env.LEDGER_POLL_MS || 250)).unref();

listen('ledger', Number(process.env.LEDGER_PORT || 3002), async (req, res, url) => {
  if (!requireInternal(req, res)) return;
  if (req.method === 'GET' && url.pathname === '/transfers') {
    const items = [...records.values()].filter(r => r.fixtureId === url.searchParams.get('userId')
      && r.transfer.sourceAccountId === url.searchParams.get('sourceAccountId')).map(r => r.transfer);
    return json(res, 200, { items, total: items.length, projectionCursor: cursor });
  }
  if (req.method === 'DELETE' && url.pathname.startsWith('/fixtures/')) {
    // Sync first: a queued completion cannot resurrect the deleted fixture after cleanup.
    await synchronize();
    const fixtureId = url.pathname.split('/')[2];
    for (const [id, entry] of records) if (entry.fixtureId === fixtureId) records.delete(id);
    return json(res, 204);
  }
  return fail(res, 404, 'NOT_FOUND');
});

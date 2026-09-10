import { randomUUID } from 'node:crypto';
import { body, fail, json, listen, requireInternal } from './common.mjs';

const fixtures = new Map();
const operations = new Map();
const events = [];
let eventSequence = 0;
const defect = process.env.LAB_DEFECT_DUPLICATE === '1';

function accountFixture(id) { return [...fixtures.values()].find(f => f.sourceAccountId === id); }
function fixturePublic(f) {
  return Object.fromEntries(['fixtureId', 'username', 'password', 'sourceAccountId', 'beneficiaryId'].map(key => [key, f[key]]));
}
function emit(type, data) { events.push({ sequence: ++eventSequence, type, data }); }

listen('accounts', Number(process.env.ACCOUNTS_PORT || 3001), async (req, res, url) => {
  if (!requireInternal(req, res)) return;
  const path = url.pathname;
  if (req.method === 'POST' && path === '/fixtures') {
    const input = await body(req);
    if (input.currency !== 'MXN' || !Number.isSafeInteger(input.balanceMinor) || input.balanceMinor < 0) {
      return fail(res, 422, 'INVALID_FIXTURE');
    }
    const fixtureId = randomUUID();
    const f = { fixtureId, username: `learner-${fixtureId}`, password: randomUUID(), sourceAccountId: randomUUID(),
      beneficiaryId: randomUUID(), currency: 'MXN', balanceMinor: input.balanceMinor, transfers: [], runId: input.runId, caseId: input.caseId };
    fixtures.set(fixtureId, f);
    return json(res, 201, fixturePublic(f));
  }
  if (req.method === 'DELETE' && path.startsWith('/fixtures/')) {
    const id = path.split('/')[2];
    fixtures.delete(id);
    for (const key of operations.keys()) if (key.startsWith(`${id}:`)) operations.delete(key);
    emit('fixture.deleted', { fixtureId: id });
    return json(res, 204);
  }
  if (req.method === 'POST' && path === '/authenticate') {
    const input = await body(req);
    const f = [...fixtures.values()].find(f => f.username === input.username && f.password === input.password);
    return f ? json(res, 200, { userId: f.fixtureId }) : fail(res, 401, 'UNAUTHENTICATED');
  }
  if (req.method === 'GET' && path === '/me') {
    const f = fixtures.get(url.searchParams.get('userId'));
    return f ? json(res, 200, { sourceAccountId: f.sourceAccountId, beneficiaryId: f.beneficiaryId }) : fail(res, 401, 'UNAUTHENTICATED');
  }
  if (req.method === 'GET' && path === '/account') {
    const f = accountFixture(url.searchParams.get('id'));
    if (!f || f.fixtureId !== url.searchParams.get('userId')) return fail(res, 403, 'FORBIDDEN');
    return json(res, 200, { id: f.sourceAccountId, currency: f.currency, balanceMinor: f.balanceMinor });
  }
  if (req.method === 'GET' && path === '/transfers') {
    const f = accountFixture(url.searchParams.get('sourceAccountId'));
    if (!f || f.fixtureId !== url.searchParams.get('userId')) return fail(res, 403, 'FORBIDDEN');
    return json(res, 200, { items: f.transfers, total: f.transfers.length });
  }
  if (req.method === 'POST' && path === '/transfers') {
    const { userId, idempotencyKey, transfer } = await body(req);
    const f = fixtures.get(userId);
    if (!f) return fail(res, 401, 'UNAUTHENTICATED');
    if (f.sourceAccountId !== transfer.sourceAccountId || f.beneficiaryId !== transfer.beneficiaryId) return fail(res, 403, 'FORBIDDEN');
    if (!idempotencyKey) return fail(res, 400, 'IDEMPOTENCY_KEY_REQUIRED');
    if (!Number.isSafeInteger(transfer.amountMinor) || transfer.amountMinor <= 0 || transfer.currency !== 'MXN') {
      return fail(res, 422, 'INVALID_AMOUNT', 'Importe inválido');
    }
    const fingerprint = JSON.stringify([transfer.sourceAccountId, transfer.beneficiaryId, transfer.currency, transfer.amountMinor]);
    const key = `${userId}:${idempotencyKey}`;
    const prior = operations.get(key);
    if (prior && !defect) {
      return prior.fingerprint === fingerprint ? json(res, 200, prior.transfer)
        : fail(res, 409, 'IDEMPOTENCY_CONFLICT', 'Clave de idempotencia reutilizada');
    }
    if (f.balanceMinor < transfer.amountMinor) return fail(res, 422, 'INSUFFICIENT_FUNDS', 'Saldo insuficiente');
    // No await in this critical section: debit, canonical record and outbox event change together.
    // This is atomic only inside this one in-memory Node process, not a production database transaction.
    const completed = { id: randomUUID(), status: 'COMPLETED', sourceAccountId: f.sourceAccountId,
      beneficiaryId: f.beneficiaryId, currency: 'MXN', amountMinor: transfer.amountMinor };
    f.balanceMinor -= completed.amountMinor;
    f.transfers.push(completed);
    operations.set(key, { fingerprint, transfer: completed });
    emit('transfer.completed', { fixtureId: f.fixtureId, transfer: completed });
    return json(res, prior && defect ? 200 : 201, completed);
  }
  if (req.method === 'GET' && path === '/outbox') {
    const after = Number(url.searchParams.get('after') || 0);
    return json(res, 200, { events: events.filter(e => e.sequence > after), latest: eventSequence });
  }
  if (req.method === 'GET' && path === '/lookup') {
    const reference = url.searchParams.get('reference');
    for (const f of fixtures.values()) {
      const t = f.transfers.find(t => t.id === reference);
      if (t) return json(res, 200, { reference: t.id, status: t.status, amountMinor: t.amountMinor,
        currency: t.currency, sourceAccountId: t.sourceAccountId, balanceMinor: f.balanceMinor });
    }
    return fail(res, 404, 'NOT_FOUND');
  }
  if (req.method === 'GET' && path === '/stats') return json(res, 200, { fixtures: fixtures.size, operations: operations.size });
  return fail(res, 404, 'NOT_FOUND');
});

import { randomUUID } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { accountsURL, body, call, fail, hookKey, json, ledgerURL, listen } from './common.mjs';

const sessions = new Map();
const html = readFileSync(new URL('../web.html', import.meta.url), 'utf8');
function session(req) {
  const id = (req.headers.cookie || '').split(';').map(s => s.trim()).find(s => s.startsWith('transferlab_session='))?.split('=')[1];
  const active = sessions.get(id);
  return active && active.expires > Date.now() ? active.userId : undefined;
}
function reply(res, response) { json(res, response.status, response.data); }
function hook(req, res) {
  if (req.headers['x-test-hook-key'] !== hookKey) { fail(res, 403, 'FORBIDDEN'); return false; }
  return true;
}

listen('gateway', Number(process.env.PORT || 3000), async (req, res, url) => {
  const path = url.pathname;
  if (req.method === 'GET' && ['/', '/transfers'].includes(path)) {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
    return res.end(html);
  }
  if (path === '/__test/lookup' && req.method === 'GET') {
    // Read-only, synthetic data, loopback-bound endpoint for the TN3270 classroom simulator.
    return reply(res, await call(`${accountsURL}/lookup?reference=${encodeURIComponent(url.searchParams.get('reference') || '')}`));
  }
  if (path.startsWith('/__test/')) {
    if (!hook(req, res)) return;
    if (path === '/__test/fixtures' && req.method === 'POST') return reply(res, await call(`${accountsURL}/fixtures`, 'POST', await body(req)));
    if (path === '/__test/stats' && req.method === 'GET') return reply(res, await call(`${accountsURL}/stats`));
    if (path.startsWith('/__test/fixtures/') && req.method === 'DELETE') {
      const id = path.split('/')[3];
      const response = await call(`${accountsURL}/fixtures/${encodeURIComponent(id)}`, 'DELETE');
      for (const [key, value] of sessions) if (value.userId === id) sessions.delete(key);
      const ledger = await call(`${ledgerURL}/fixtures/${encodeURIComponent(id)}`, 'DELETE');
      return reply(res, ledger.status === 204 ? response : ledger);
    }
    return fail(res, 404, 'NOT_FOUND');
  }
  if (path === '/api/session' && req.method === 'POST') {
    const response = await call(`${accountsURL}/authenticate`, 'POST', await body(req));
    if (response.status !== 200) return reply(res, response);
    const id = randomUUID();
    sessions.set(id, { userId: response.data.userId, expires: Date.now() + 30 * 60 * 1000 });
    return json(res, 200, response.data, { 'Set-Cookie': `transferlab_session=${id}; HttpOnly; SameSite=Lax; Path=/; Max-Age=1800` });
  }
  if (path.startsWith('/api/')) {
    const userId = session(req);
    if (!userId) return fail(res, 401, 'UNAUTHENTICATED', 'Inicia sesión con los datos sintéticos de tu fixture.');
    if (path === '/api/me' && req.method === 'GET') return reply(res, await call(`${accountsURL}/me?userId=${userId}`));
    if (path.startsWith('/api/accounts/') && req.method === 'GET') return reply(res,
      await call(`${accountsURL}/account?userId=${userId}&id=${encodeURIComponent(path.split('/')[3])}`));
    if (path === '/api/transfers' && req.method === 'POST') return reply(res, await call(`${accountsURL}/transfers`, 'POST', {
      userId, idempotencyKey: req.headers['idempotency-key'], transfer: await body(req),
    }));
    if (['/api/transfers', '/api/ledger/transfers'].includes(path) && req.method === 'GET') {
      const sourceAccountId = encodeURIComponent(url.searchParams.get('sourceAccountId') || '');
      const authorization = await call(`${accountsURL}/account?userId=${userId}&id=${sourceAccountId}`);
      if (authorization.status !== 200) return reply(res, authorization);
      return reply(res, await call(`${path.includes('/ledger/') ? ledgerURL : accountsURL}/transfers?userId=${userId}&sourceAccountId=${sourceAccountId}`));
    }
  }
  return fail(res, 404, 'NOT_FOUND');
});

import http from 'node:http';

export const accountsURL = `http://127.0.0.1:${process.env.ACCOUNTS_PORT || 3001}`;
export const ledgerURL = `http://127.0.0.1:${process.env.LEDGER_PORT || 3002}`;
export const serviceKey = process.env.LAB_SERVICE_KEY || 'synthetic-local-service-only';
export const hookKey = process.env.TEST_HOOK_KEY;
if (!hookKey) throw new Error('Set TEST_HOOK_KEY for the local classroom simulator.');

export function json(res, status, data, headers = {}) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...headers });
  res.end(status === 204 ? undefined : JSON.stringify(data));
}
export function fail(res, status, code, message = code) { json(res, status, { code, message }); }
export async function body(req) {
  let text = '';
  for await (const chunk of req) {
    text += chunk;
    if (text.length > 65536) throw new Error('Request exceeds the classroom size limit.');
  }
  return text ? JSON.parse(text) : {};
}
export function requireInternal(req, res) {
  if (req.headers['x-service-key'] !== serviceKey) { fail(res, 403, 'FORBIDDEN'); return false; }
  return true;
}
export async function call(url, method = 'GET', data) {
  const response = await fetch(url, {
    method, headers: { 'Content-Type': 'application/json', 'X-Service-Key': serviceKey },
    ...(data === undefined ? {} : { body: JSON.stringify(data) }), signal: AbortSignal.timeout(2500),
  });
  return { status: response.status, data: response.status === 204 ? null : await response.json() };
}
export function listen(name, port, handler) {
  const server = http.createServer(async (req, res) => {
    try {
      const url = new URL(req.url, `http://127.0.0.1:${port}`);
      if (url.pathname === '/health') {
        return json(res, 200, { status: 'ok', environment: 'test', contractVersion: '1', service: name });
      }
      await handler(req, res, url);
    } catch (error) {
      console.error(JSON.stringify({ service: name, message: error.message }));
      if (!res.headersSent) fail(res, 503, 'SERVICE_UNAVAILABLE', 'Servicio temporalmente no disponible');
      else res.end();
    }
  });
  server.listen(port, '127.0.0.1', () => console.log(JSON.stringify({ service: name, port, pid: process.pid })));
  server.on('error', error => { console.error(error.message); process.exit(1); });
  return server;
}

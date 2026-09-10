import { spawn } from 'node:child_process';
import { createServer } from 'node:net';
import { randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const args = process.argv.slice(2);
if (args.includes('--help')) {
  console.log('node scripts/start-demo.mjs [--port=3300] [--verify]\nStarts an isolated synthetic TransferLab. Ctrl+C stops its three services.');
  process.exit(0);
}
if (args.some(arg => arg !== '--verify' && !/^--port=\d+$/.test(arg))) throw new Error('Unknown option. Use --help.');
if (Number(process.versions.node.split('.')[0]) < 22) throw new Error('Node.js 22 or later is required.');
const port = Number(args.find(arg => arg.startsWith('--port='))?.slice(7) || 3300);
if (!Number.isInteger(port) || port < 1024 || port > 65533) throw new Error('Choose a base port from 1024 to 65533.');
const baseURL = `http://127.0.0.1:${port}`;
const key = 'classroom-demo-only';
const children = [];
let stopping = false;
let childFailure;
function stop() {
  stopping = true;
  for (const child of children) if (child.exitCode === null) child.kill();
}
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => { stop(); process.exit(0); });
process.on('exit', stop);
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function request(path, { method = 'GET', data, cookie, hook = false } = {}) {
  const response = await fetch(baseURL + path, {
    method, headers: { 'Content-Type': 'application/json', ...(hook ? { 'X-Test-Hook-Key': key } : {}), ...(cookie ? { Cookie: cookie } : {}) },
    ...(data === undefined ? {} : { body: JSON.stringify(data) }), signal: AbortSignal.timeout(5000),
  });
  return { status: response.status, data: response.status === 204 ? null : await response.json(), cookie: response.headers.get('set-cookie')?.split(';')[0] };
}
try {
  for (const candidate of [port, port + 1, port + 2]) {
    await new Promise((resolve, reject) => {
      const probe = createServer();
      probe.once('error', () => reject(new Error(`Port ${candidate} is occupied. Use a different --port; existing services were not stopped.`)));
      probe.listen(candidate, '127.0.0.1', () => probe.close(resolve));
    });
  }
  const env = { ...process.env, PORT: String(port), ACCOUNTS_PORT: String(port + 1), LEDGER_PORT: String(port + 2),
    TEST_HOOK_KEY: key, LAB_SERVICE_KEY: 'synthetic-local-service-only', LAB_DEFECT_DUPLICATE: '0' };
  for (const name of ['accounts', 'ledger', 'gateway']) {
    const child = spawn(process.execPath, [fileURLToPath(new URL(`../videos/lab/distributed/services/${name}.mjs`, import.meta.url))],
      { env, windowsHide: true, stdio: 'inherit' });
    children.push(child);
    child.once('error', error => { childFailure = error; });
    child.once('exit', code => {
      if (!stopping) { console.error(`${name} exited unexpectedly (${code}).`); stop(); process.exitCode = 1; }
    });
  }
  for (const [name, candidate] of [['gateway', port], ['accounts', port + 1], ['ledger', port + 2]]) {
    const deadline = Date.now() + 15000;
    let ready = false;
    while (!ready && Date.now() < deadline) {
      if (childFailure || stopping) throw childFailure || new Error('A service stopped during startup.');
      try {
        const response = await fetch(`http://127.0.0.1:${candidate}/health`, { signal: AbortSignal.timeout(500) });
        const health = await response.json();
        ready = response.ok && health.service === name && health.status === 'ok';
      } catch { /* Retry readiness only, with a fixed deadline. */ }
      if (!ready) await sleep(100);
    }
    if (!ready) throw new Error(`${name} did not become healthy within 15 seconds.`);
  }
  const fixtureResponse = await request('/__test/fixtures', { method: 'POST', hook: true,
    data: { runId: randomUUID(), caseId: 'manual-demo', currency: 'MXN', balanceMinor: 100000 } });
  assert.equal(fixtureResponse.status, 201);
  const fixture = fixtureResponse.data;
  if (args.includes('--verify')) {
    const page = await fetch(baseURL + '/transfers');
    assert.equal(page.status, 200); assert.match(await page.text(), /TransferLab/);
    const login = await request('/api/session', { method: 'POST', data: { username: fixture.username, password: fixture.password } });
    assert.equal(login.status, 200); assert.ok(login.cookie);
    const transfer = { sourceAccountId: fixture.sourceAccountId, beneficiaryId: fixture.beneficiaryId, amountMinor: 10000, currency: 'MXN' };
    const idempotencyKey = randomUUID();
    const send = async () => {
      const response = await fetch(baseURL + '/api/transfers', { method: 'POST',
        headers: { 'Content-Type': 'application/json', Cookie: login.cookie, 'Idempotency-Key': idempotencyKey },
        body: JSON.stringify(transfer), signal: AbortSignal.timeout(5000) });
      return { status: response.status, data: await response.json() };
    };
    const first = await send(); assert.equal(first.status, 201); assert.ok(first.data.id);
    const replay = await send(); assert.equal(replay.status, 200); assert.equal(replay.data.id, first.data.id);
    const account = await request(`/api/accounts/${fixture.sourceAccountId}`, { cookie: login.cookie });
    assert.equal(account.status, 200); assert.equal(account.data.balanceMinor, 90000);
    const canonical = await request(`/api/transfers?sourceAccountId=${fixture.sourceAccountId}`, { cookie: login.cookie });
    assert.equal(canonical.data.total, 1); assert.equal(canonical.data.items[0].id, first.data.id);
    const deadline = Date.now() + 5000;
    let projected = false;
    while (Date.now() < deadline && !projected) {
      const result = await request(`/api/ledger/transfers?sourceAccountId=${fixture.sourceAccountId}`, { cookie: login.cookie });
      projected = result.status === 200 && result.data.items.some(item => item.id === first.data.id);
      if (!projected) await sleep(100);
    }
    assert.ok(projected, 'The exact transfer must reach the independent ledger.');
    assert.equal((await request(`/__test/fixtures/${fixture.fixtureId}`, { method: 'DELETE', hook: true })).status, 204);
    assert.equal((await request('/api/me', { cookie: login.cookie })).status, 401);
    console.log(JSON.stringify({ verified: true, services: 3, html: 'passed', transfer: 'passed', sequentialReplay: 'passed', ledger: 'passed', cleanup: 'passed', browserAutomation: 'not run by this smoke check' }));
    stop();
  } else {
    console.log(`\nTransferLab READY: ${baseURL}/transfers\nSynthetic demo username: ${fixture.username}\nSynthetic demo password: ${fixture.password}\nOpening balance: MXN 1,000.00\nTest BASE_URL: ${baseURL}\nTest TEST_HOOK_KEY: ${key}\nCtrl+C stops this demo and discards its in-memory data.\n`);
  }
} catch (error) {
  console.error(error.message); stop(); process.exitCode = 1;
}

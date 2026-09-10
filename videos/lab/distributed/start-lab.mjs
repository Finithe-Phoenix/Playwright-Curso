import { spawn } from 'node:child_process';
import { createServer } from 'node:net';
import { mkdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

if (!process.env.TEST_HOOK_KEY) throw new Error('Set TEST_HOOK_KEY before starting the local simulator.');
const definitions = [ ['accounts', Number(process.env.ACCOUNTS_PORT || 3001)],
  ['ledger', Number(process.env.LEDGER_PORT || 3002)], ['gateway', Number(process.env.PORT || 3000)] ];

// Check all target ports before creating any child; do not reuse or stop another application's server.
for (const [name, port] of definitions) {
  await new Promise((resolve, reject) => {
    const probe = createServer(); probe.once('error', () => reject(new Error(`${name}: port ${port} is already in use.`)));
    probe.listen(port, '127.0.0.1', () => probe.close(resolve));
  });
}
const children = definitions.map(([name, port]) => {
  const child = spawn(process.execPath, [fileURLToPath(new URL(`./services/${name}.mjs`, import.meta.url))],
    { cwd: new URL('.', import.meta.url), env: process.env, stdio: 'inherit', windowsHide: true });
  return { name, port, child };
});
let stopping = false;
function stop() { if(stopping) return; stopping = true; for (const {child} of children) child.kill(); }
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => { stop(); process.exit(0); });
for (const {name,child} of children) child.once('exit', code => { if(!stopping) { console.error(`${name} exited (${code}).`); stop(); process.exit(code || 1); } });
process.on('exit', stop);
mkdirSync(new URL('.runtime/', import.meta.url), { recursive:true });
writeFileSync(new URL(`.runtime/processes-${process.env.PORT || 3000}.json`, import.meta.url), JSON.stringify({parent:process.pid, children:children.map(({name,port,child})=>({name,port,pid:child.pid})),startedAt:new Date().toISOString()},null,2));
const deadline = Date.now() + 15000;
for (const {name,port} of children) {
  let ready = false;
  while(Date.now()<deadline) {
    try { const r = await fetch(`http://127.0.0.1:${port}/health`, {signal:AbortSignal.timeout(500)}); if(r.ok) {ready=true;break;} } catch {}
    await new Promise(resolve=>setTimeout(resolve,100));
  }
  if(!ready) {stop();throw new Error(`${name} did not become ready within 15 seconds.`);}
}
console.log(`TransferLab READY: http://127.0.0.1:${process.env.PORT || 3000}/transfers (synthetic classroom only)`);

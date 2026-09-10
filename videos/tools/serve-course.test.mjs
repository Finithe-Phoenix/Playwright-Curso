import assert from 'node:assert/strict';
import http from 'node:http';
import { once } from 'node:events';
import { mkdtemp, mkdir, writeFile, symlink, rm, realpath } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { createCourseServer } from './serve-course.mjs';

function request(port, target, options = {}) {
  return new Promise((resolve, reject) => {
    const req = http.request({ hostname: '127.0.0.1', port, path: target, ...options }, res => {
      const chunks = [];
      res.on('data', chunk => chunks.push(chunk));
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body: Buffer.concat(chunks) }));
    });
    req.on('error', reject); req.end();
  });
}

test('course HTTP server supports seeking and confines real paths', async t => {
  const temporary = await mkdtemp(path.join(os.tmpdir(), 'playwright-course-range-'));
  const root = path.join(temporary, 'public');
  const outside = path.join(temporary, 'outside');
  await mkdir(root); await mkdir(outside);
  const bytes = Buffer.from(Array.from({ length: 1024 }, (_, i) => i % 251));
  await writeFile(path.join(root, 'movie.mp4'), bytes);
  await writeFile(path.join(root, 'index.html'), '<title>Range test</title>');
  await writeFile(path.join(root, 'lesson.md'), '# Lesson');
  await writeFile(path.join(root, 'empty.mp4'), '');
  await writeFile(path.join(outside, 'secret.txt'), 'must never be served');
  await symlink(outside, path.join(root, 'escape'), process.platform === 'win32' ? 'junction' : 'dir');
  const server = await createCourseServer({ root });
  server.listen(8767, '127.0.0.1');
  try {
    await once(server, 'listening');
    await t.test('full GET and MIME headers', async () => {
      const result = await request(8767, '/movie.mp4');
      assert.equal(result.status, 200); assert.deepEqual(result.body, bytes);
      assert.equal(result.headers['accept-ranges'], 'bytes'); assert.equal(result.headers['content-type'], 'video/mp4');
      assert.match((await request(8767, '/lesson.md')).headers['content-type'], /^text\/plain/);
    });
    await t.test('middle, open, suffix and clipped ranges return exact bytes', async () => {
      for (const [header, start, end] of [['bytes=100-199', 100, 199], ['bytes=900-', 900, 1023], ['bytes=-12', 1012, 1023], ['bytes=1000-9999', 1000, 1023]]) {
        const result = await request(8767, '/movie.mp4', { headers: { Range: header } });
        assert.equal(result.status, 206); assert.equal(result.headers['content-range'], `bytes ${start}-${end}/1024`);
        assert.equal(Number(result.headers['content-length']), end - start + 1); assert.deepEqual(result.body, bytes.subarray(start, end + 1));
      }
    });
    await t.test('HEAD has complete metadata and no body', async () => {
      const result = await request(8767, '/movie.mp4', { method: 'HEAD', headers: { Range: 'bytes=0-9' } });
      assert.equal(result.status, 200); assert.equal(Number(result.headers['content-length']), 1024); assert.equal(result.body.length, 0);
    });
    await t.test('invalid, unsatisfiable and unsupported ranges return 416', async () => {
      for (const range of ['bytes=1024-', 'bytes=3-2', 'bytes=-0', 'bytes=0-1,4-5', 'bytes=9007199254740999-', 'items=0-1']) {
        const result = await request(8767, '/movie.mp4', { headers: { Range: range } });
        assert.equal(result.status, 416); assert.equal(result.headers['content-range'], 'bytes */1024'); assert.equal(result.body.length, 0);
      }
      assert.equal((await request(8767, '/empty.mp4', { headers: { Range: 'bytes=0-' } })).status, 416);
    });
    await t.test('If-Range mismatch returns full resource', async () => {
      const result = await request(8767, '/movie.mp4', { headers: { Range: 'bytes=0-9', 'If-Range': '"stale"' } });
      assert.equal(result.status, 200); assert.deepEqual(result.body, bytes);
    });
    await t.test('traversal, alternate separators and external junction are rejected', async () => {
      for (const target of ['/../outside/secret.txt', '/%2e%2e/outside/secret.txt', '/%5c..%5coutside%5csecret.txt', '/escape/secret.txt', '/movie.mp4%3Ahidden', '/%00']) {
        assert.equal((await request(8767, target)).status, 403, target);
      }
      assert.equal((await request(8767, '/%xx')).status, 400);
    });
    await t.test('missing resource and unsupported method are explicit', async () => {
      assert.equal((await request(8767, '/missing')).status, 404);
      assert.equal((await request(8767, '/', { method: 'POST' })).status, 405);
      assert.equal((await request(8767, '/')).status, 200);
    });
  } finally {
    await new Promise(resolve => { server.close(resolve); server.closeAllConnections(); });
    const resolved = await realpath(temporary);
    const tempRoot = await realpath(os.tmpdir());
    assert.equal(path.dirname(resolved).toLowerCase(), tempRoot.toLowerCase());
    assert.ok(path.basename(resolved).startsWith('playwright-course-range-'));
    await rm(resolved, { recursive: true, force: true });
  }
});

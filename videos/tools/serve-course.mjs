/** Local course server with byte ranges so video chapters can seek immediately. */
import http from 'node:http';
import { createReadStream } from 'node:fs';
import { realpath, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const WORK_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const MIME = {
  '.html': 'text/html; charset=utf-8', '.htm': 'text/html; charset=utf-8',
  '.mp4': 'video/mp4', '.webm': 'video/webm', '.wav': 'audio/wav', '.mp3': 'audio/mpeg',
  '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.md': 'text/plain; charset=utf-8', '.txt': 'text/plain; charset=utf-8',
  '.srt': 'application/x-subrip; charset=utf-8', '.vtt': 'text/vtt; charset=utf-8',
  '.ttf': 'font/ttf', '.otf': 'font/otf', '.woff': 'font/woff', '.woff2': 'font/woff2',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
  '.pdf': 'application/pdf', '.zip': 'application/zip', '.xml': 'application/xml; charset=utf-8',
};

function inside(root, candidate) {
  const relative = path.relative(root, candidate);
  return relative === '' || (!relative.startsWith(`..${path.sep}`) && relative !== '..' && !path.isAbsolute(relative));
}

function reply(response, status, message, method = 'GET', extra = {}) {
  const payload = Buffer.from(message);
  response.writeHead(status, { 'Content-Type': 'text/plain; charset=utf-8', 'Content-Length': payload.length,
    'X-Content-Type-Options': 'nosniff', ...extra });
  response.end(method === 'HEAD' ? undefined : payload);
}

/** A single byte range; invalid or multiple ranges return null. */
export function parseRange(value, size) {
  const match = /^bytes=(\d*)-(\d*)$/.exec(value.trim());
  if (!match || (!match[1] && !match[2]) || size === 0) return null;
  const first = match[1] ? Number(match[1]) : null;
  const last = match[2] ? Number(match[2]) : null;
  if ((first !== null && !Number.isSafeInteger(first)) || (last !== null && !Number.isSafeInteger(last))) return null;
  if (first === null) return last > 0 ? { start: Math.max(0, size - last), end: size - 1 } : null;
  if (first >= size || (last !== null && last < first)) return null;
  return { start: first, end: last === null ? size - 1 : Math.min(size - 1, last) };
}

export async function createCourseServer({ root = WORK_ROOT } = {}) {
  const canonicalRoot = await realpath(root);
  return http.createServer(async (request, response) => {
    const method = request.method ?? 'GET';
    if (!['GET', 'HEAD'].includes(method)) {
      reply(response, 405, 'Only GET and HEAD are supported.\n', method, { Allow: 'GET, HEAD' });
      return;
    }
    try {
      // Decode the raw path before normalization; URL() would hide ../ sequences.
      const raw = (request.url ?? '/').split('?')[0];
      if (!raw.startsWith('/')) { reply(response, 400, 'Invalid request target.\n', method); return; }
      let decoded;
      try { decoded = decodeURIComponent(raw); }
      catch { reply(response, 400, 'Invalid URL encoding.\n', method); return; }
      // Block NUL, Windows drive/alternate-data-stream notation and path escapes.
      if (/[\0:]/.test(decoded)) { reply(response, 403, 'Path is outside the course.\n', method); return; }
      decoded = decoded.replaceAll('\\', '/');
      const segments = decoded.split('/');
      if (segments.includes('..')) { reply(response, 403, 'Path is outside the course.\n', method); return; }
      let candidate = path.resolve(canonicalRoot, `.${decoded}`);
      if (!inside(canonicalRoot, candidate)) { reply(response, 403, 'Path is outside the course.\n', method); return; }
      let actual = await realpath(candidate);
      if (!inside(canonicalRoot, actual)) { reply(response, 403, 'Link is outside the course.\n', method); return; }
      let info = await stat(actual);
      if (info.isDirectory()) {
        if (!decoded.endsWith('/')) {
          response.writeHead(301, { Location: `${raw}/${(request.url ?? '').includes('?') ? `?${request.url.split('?').slice(1).join('?')}` : ''}`, 'Content-Length': 0 });
          response.end(); return;
        }
        candidate = path.join(actual, 'index.html');
        actual = await realpath(candidate);
        if (!inside(canonicalRoot, actual)) { reply(response, 403, 'Link is outside the course.\n', method); return; }
        info = await stat(actual);
      }
      if (!info.isFile()) { reply(response, 404, 'File not found.\n', method); return; }
      const etag = `"${info.size.toString(16)}-${Math.trunc(info.mtimeMs).toString(16)}"`;
      const modified = info.mtime.toUTCString();
      const headers = { 'Content-Type': MIME[path.extname(actual).toLowerCase()] ?? 'application/octet-stream',
        'Accept-Ranges': 'bytes', 'Last-Modified': modified, ETag: etag,
        'Cache-Control': 'no-cache', 'X-Content-Type-Options': 'nosniff' };
      if (request.headers['if-none-match'] === etag && !request.headers.range) {
        response.writeHead(304, headers); response.end(); return;
      }
      let range = null;
      // RFC range semantics apply to GET. HEAD describes the complete resource.
      if (method === 'GET' && request.headers.range) {
        const ifRange = request.headers['if-range'];
        if (!ifRange || ifRange === etag || ifRange === modified) {
          range = parseRange(request.headers.range, info.size);
          if (!range) {
            response.writeHead(416, { ...headers, 'Content-Range': `bytes */${info.size}`, 'Content-Length': 0 });
            response.end(); return;
          }
        }
      }
      if (range) headers['Content-Range'] = `bytes ${range.start}-${range.end}/${info.size}`;
      headers['Content-Length'] = range ? range.end - range.start + 1 : info.size;
      response.writeHead(range ? 206 : 200, headers);
      if (method === 'HEAD' || info.size === 0) { response.end(); return; }
      const stream = createReadStream(actual, range ?? undefined);
      stream.on('error', () => response.destroy());
      response.on('close', () => stream.destroy());
      stream.pipe(response);
    } catch (error) {
      if (!response.headersSent) reply(response, ['ENOENT', 'ENOTDIR'].includes(error.code) ? 404 : 500,
        ['ENOENT', 'ENOTDIR'].includes(error.code) ? 'File not found.\n' : 'Unable to read course file.\n', method);
      else response.destroy();
    }
  });
}

async function main() {
  const args = process.argv.slice(2);
  if (args.includes('--help')) {
    console.log('node tools/serve-course.mjs [--port 8766]\nServes the work folder at 127.0.0.1 with video byte ranges.'); return;
  }
  if (args.length && (args.length !== 2 || args[0] !== '--port')) throw new Error('Use --port NUMBER or --help.');
  const port = args.length ? Number(args[1]) : 8766;
  if (!Number.isInteger(port) || port < 1024 || port > 65535) throw new Error('Port must be an integer from 1024 to 65535.');
  const server = await createCourseServer();
  server.on('error', error => {
    console.error(error.code === 'EADDRINUSE' ? `Port ${port} is already in use; choose another with --port. No process was stopped.` : error.message);
    process.exitCode = 1;
  });
  server.listen(port, '127.0.0.1', () => console.log(JSON.stringify({ status: 'listening',
    url: `http://127.0.0.1:${port}/videos/index.html`, root: WORK_ROOT, byteRanges: true })));
  for (const signal of ['SIGINT', 'SIGTERM']) process.once(signal, () => {
    server.close(() => process.exit(0));
    server.closeAllConnections();
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch(error => { console.error(error.message); process.exitCode = 1; });
}

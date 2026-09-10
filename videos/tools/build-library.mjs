import { existsSync, readFileSync, statSync, writeFileSync, openSync, readSync, closeSync } from 'node:fs';
import { dirname, join, relative, resolve, sep, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';

// Run after an episode finishes, and once with --strict before handing over all 12.
const root = dirname(dirname(fileURLToPath(import.meta.url)));
const args = process.argv.slice(2);
const strict = args.includes('--strict');
const probeArg = args.indexOf('--ffprobe');
if (probeArg !== -1 && !args[probeArg + 1]) throw new Error('--ffprobe requires an executable path.');
const probeCandidates = [probeArg >= 0 && args[probeArg + 1], process.env.FFPROBE_PATH, 'ffprobe',
  process.env.LOCALAPPDATA && join(process.env.LOCALAPPDATA, 'Microsoft', 'WinGet', 'Links', 'ffprobe.exe')].filter(Boolean);
const ffprobe = probeCandidates.find(executable => spawnSync(executable, ['-version'],
  { encoding: 'utf8', windowsHide: true, timeout: 10000 }).status === 0);
const jsonFile = path => existsSync(path) ? JSON.parse(readFileSync(path, 'utf8').replace(/^\uFEFF/, '')) : null;
const isFile = path => existsSync(path) && statSync(path).isFile() && statSync(path).size > 0;
const hashCache = new Map();
function fileHash(path) {
  if (hashCache.has(path)) return hashCache.get(path);
  if (!isFile(path)) return null;
  const digest = createHash('sha256');
  const descriptor = openSync(path, 'r');
  const buffer = Buffer.allocUnsafe(1024 * 1024);
  try {
    for (let count; (count = readSync(descriptor, buffer)) > 0;) digest.update(buffer.subarray(0, count));
  } finally { closeSync(descriptor); }
  const value = digest.digest('hex');
  hashCache.set(path, value);
  return value;
}
function currentInputs(checkpoint) {
  if (!checkpoint?.inputFiles || !checkpoint.inputFiles['tools/build_compositions.py']) return false;
  return Object.entries(checkpoint.inputFiles).every(([name, expected]) => {
    const candidate = resolve(root, name);
    const within = relative(root, candidate);
    return within && within !== '..' && !within.startsWith(`..${sep}`) && !isAbsolute(within) &&
      /^[a-f0-9]{64}$/.test(expected) && fileHash(candidate) === expected;
  });
}
const url = path => relative(root, path).split(/[\\/]/).map(encodeURIComponent).join('/');
const entries = jsonFile(join(root, 'scripts', 'episodes.json')) || [];
const production = jsonFile(join(root, 'production-progress.json'));
if (!Array.isArray(entries)) throw new Error('scripts/episodes.json must contain an array.');
const seen = new Set();
for (const entry of entries) {
  if (!/^\d{2}$/.test(entry.id) || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(entry.slug)) throw new Error('Invalid episode ID or slug.');
  if (seen.has(entry.id)) throw new Error(`Duplicate episode ${entry.id}.`);
  seen.add(entry.id);
}

function inspectVideo(path) {
  if (!isFile(path)) return { status: 'pending', label: 'En preparación', playable: false };
  if (!ffprobe) return { status: 'unverified', label: 'Archivo sin verificar', playable: true };
  const check = spawnSync(ffprobe, ['-v', 'error', '-show_format', '-show_streams', '-of', 'json', path],
    { encoding: 'utf8', windowsHide: true, timeout: 30000, maxBuffer: 1024 * 1024 });
  if (check.status !== 0) return { status: 'incomplete', label: 'Render incompleto', playable: false };
  let result;
  try { result = JSON.parse(check.stdout); } catch { return { status: 'incomplete', label: 'Render incompleto', playable: false }; }
  const video = result.streams?.find(stream => stream.codec_type === 'video');
  const audio = result.streams?.find(stream => stream.codec_type === 'audio');
  const duration = Number(result.format?.duration);
  if (!video || !audio || !Number.isFinite(duration) || duration <= 0) {
    return { status: 'incomplete', label: !audio ? 'Voz pendiente' : 'Render incompleto', playable: !!video };
  }
  const inRange = duration >= 360 && duration <= 480;
  return { status: inRange ? 'ready' : 'duration-review', label: inRange ? 'Disponible' : 'Revisar duración',
    playable: true, duration, width: video.width, height: video.height, videoCodec: video.codec_name,
    audioCodec: audio.codec_name, bytes: statSync(path).size };
}

const lessons = Array.from({ length: 12 }, (_, i) => {
  const id = String(i + 1).padStart(2, '0');
  const entry = entries.find(item => item.id === id);
  if (!entry) return { id, title: `Episodio ${id}`, summary: 'El contenido se está preparando.', status: 'pending',
    label: 'En preparación', playable: false, scenes: [], objectives: [], sources: [] };
  const name = `${id}-${entry.slug}`;
  const render = join(root, 'renders', `${name}.mp4`);
  const timeline = jsonFile(join(root, 'audio', id, 'timeline.json'));
  const srt = join(root, 'audio', id, 'subtitles.srt');
  const script = join(root, 'compositions', name, 'SCRIPT.md');
  const status = inspectVideo(render);
  const checkpoint = production?.episodes?.[id];
  if (status.status === 'ready' && checkpoint) {
    if (checkpoint.stage !== 'rendered' || !checkpoint.artifact || !currentInputs(checkpoint) ||
        checkpoint.artifact.sha256 !== fileHash(render)) {
      Object.assign(status, { status: 'updating', label: 'Actualizándose', playable: false });
    }
  }
  const scenes = (entry.scenes || []).map(scene => {
    const timing = timeline?.scenes?.find(item => item.id === scene.id);
    return { ...scene, start: Number.isFinite(timing?.start) ? timing.start : null };
  });
  const captions = isFile(srt) ? readFileSync(srt, 'utf8').replace(/^\uFEFF/, '') : '';
  return { id, slug: entry.slug, title: entry.title, summary: entry.summary,
    objectives: entry.objectives || [], sources: entry.sources || [], scenes, ...status,
    render: isFile(render) ? url(render) : null,
    script: isFile(script) ? url(script) : null,
    captions, subtitles: captions ? url(srt) : null,
    fullSource: 'scripts/episodes.json',
  };
});
const ready = lessons.filter(lesson => lesson.status === 'ready').length;
const totalDuration = lessons.filter(lesson => lesson.status === 'ready').reduce((sum, lesson) => sum + lesson.duration, 0);
const qaReport = jsonFile(join(root, 'qa', 'final-validation.json'));
// The previous review cannot approve a changed design or an older render.
const designUpdatedAt = Math.max(statSync(fileURLToPath(import.meta.url)).mtimeMs,
  statSync(join(root, 'tools', 'build_compositions.py')).mtimeMs);
const qaIsCurrent = ready === 12 && qaReport?.ready === true && qaReport?.videos?.length === 12 &&
  Date.parse(qaReport.generatedAtUtc) >= designUpdatedAt && lessons.every(lesson => {
    const reviewed = qaReport.videos.find(item => item.episode === lesson.id);
    const checkpoint = production?.episodes?.[lesson.id];
    return reviewed && checkpoint?.inputHash === reviewed.inputHash && checkpoint?.artifact?.sha256 === reviewed.sha256 &&
      reviewed.visualReview?.mp4Sha256 === reviewed.sha256 && reviewed.visualReview?.status === 'passed_for_sampled_frames';
  });
const finalQA = qaIsCurrent && isFile(join(root, 'qa', 'VIDEO-REVIEW.md')) ? 'qa/VIDEO-REVIEW.md' : null;
const qaStatus = finalQA ? 'current' : qaReport ? 'review-required' : 'pending';
const data = JSON.stringify({ lessons, ready, totalDuration, finalQA, qaStatus, design: 'blue-gray-white', generatedAt: new Date().toISOString() })
  .replace(/</g, '\\u003c').replace(/>/g, '\\u003e').replace(/&/g, '\\u0026');

const html = `<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Playwright + IA · Biblioteca de videos</title>
<meta name="description" content="Doce lecciones avanzadas de Playwright con voz en inglés, ejemplos en TypeScript, Python y Java, aplicaciones distribuidas y un laboratorio TN3270 con IBM tnz.">
<style>
:root{--paper:#F4F7FC;--ink:#14213D;--blue:#2457E6;--line:#D7DFED;--soft:#EAF0FF;--muted:#56647A;--white:#FFFFFF;--code:#111C34;--code-text:#EEF3FF;color:var(--ink);background:var(--paper);font-family:Segoe UI,Arial,sans-serif;font-synthesis:none}
*{box-sizing:border-box}body{margin:0}a{color:var(--blue);text-underline-offset:4px}button,input{font:inherit}button,a,input,video,summary{outline-offset:4px}button:focus-visible,a:focus-visible,input:focus-visible,summary:focus-visible{outline:3px solid var(--blue)}button{cursor:pointer}button:disabled{cursor:default;opacity:.45}
header{padding:40px max(28px,calc((100vw - 1540px)/2)) 30px;border-bottom:1px solid var(--line);background:var(--white);border-top:5px solid var(--blue)}.brand{font-size:12px;letter-spacing:2px;font-weight:800;color:var(--blue)}.headerline{display:flex;justify-content:space-between;gap:28px;align-items:center}h1{font-size:clamp(32px,3.4vw,50px);line-height:1.08;letter-spacing:-1.7px;margin:16px 0;font-weight:750}header p{color:var(--muted);line-height:1.75;margin:0;max-width:820px}.badge{display:inline-flex;align-items:center;white-space:nowrap;background:var(--soft);color:var(--blue);border:1px solid var(--line);border-radius:12px;padding:13px 17px;font-size:14px;font-weight:700}.toplinks{display:flex;gap:10px;flex-wrap:wrap;margin-top:26px;font-size:13px}.toplinks a{padding:9px 13px;border:1px solid var(--line);border-radius:8px;text-decoration:none;font-weight:600}.toplinks a:hover{background:var(--soft);border-color:var(--blue)}
.layout{display:grid;grid-template-columns:330px minmax(0,1fr);gap:28px;max-width:1596px;margin:auto;padding:30px 28px 65px}.sidebar{background:var(--white);padding:22px 16px;border:1px solid var(--line);border-radius:16px}.sidebar h2{font-size:12px;text-transform:uppercase;letter-spacing:1.8px;margin:0 7px 17px;color:var(--muted)}.search{width:100%;padding:13px 14px;border:1px solid var(--line);border-radius:9px;background:var(--paper);color:var(--ink);margin-bottom:17px}.search::placeholder{color:var(--muted)}.lessonlist{display:flex;flex-direction:column;gap:8px}.lesson{display:grid;grid-template-columns:35px 1fr;gap:11px;text-align:left;border:1px solid var(--line);border-radius:10px;padding:14px 11px;background:var(--white);color:var(--ink);width:100%;line-height:1.45}.lesson:hover{background:var(--paper);border-color:var(--blue)}.lesson[aria-current=true]{background:var(--soft);border-color:var(--blue);box-shadow:inset 3px 0 0 var(--blue)}.number{font-weight:750;color:var(--blue);font-size:13px;display:flex;align-items:center;justify-content:center;background:var(--paper);border:1px solid var(--line);border-radius:7px;height:32px}.lesson[aria-current=true] .number{background:var(--blue);color:var(--white);border-color:var(--blue)}.lesson strong{font-size:14px;display:block;font-weight:650}.lesson small{color:var(--muted);display:block;font-size:12px;margin-top:8px}.status-dot{display:inline-block;width:6px;height:6px;background:var(--muted);border-radius:99px;margin-right:6px}.status-dot.ready{background:var(--blue)}
.content{min-width:0;background:var(--white);border:1px solid var(--line);border-radius:18px;padding:24px;box-shadow:0 8px 30px rgba(20,33,61,.035)}.screen{background:var(--code);border:1px solid var(--line);border-radius:12px;overflow:hidden;position:relative;aspect-ratio:16/9;display:flex;align-items:center;justify-content:center}video{display:block;width:100%;height:100%;background:var(--code)}video::cue{background:rgba(17,28,52,.94);color:var(--code-text);font-family:Segoe UI,Arial,sans-serif}.waiting{position:absolute;color:var(--code-text);text-align:center;max-width:510px;padding:30px}.waiting strong{font-size:clamp(22px,2.5vw,33px);display:block;line-height:1.2}.waiting p{font-size:15px;line-height:1.75;color:var(--code-text)}.controls{display:flex;justify-content:space-between;gap:18px;margin:18px 0 30px;align-items:center}.controls button,.copy{border:1px solid var(--line);background:var(--white);border-radius:8px;padding:10px 15px;color:var(--ink);font-size:13px;font-weight:650}.controls button:hover:not(:disabled),.copy:hover{color:var(--blue);background:var(--soft);border-color:var(--blue)}.meta{font-size:12px;color:var(--muted);line-height:1.7}.lessonhead{display:flex;gap:20px;align-items:flex-start}.lessonhead h2{font-size:clamp(27px,2.6vw,38px);font-weight:750;line-height:1.18;letter-spacing:-.8px;margin:10px 0 16px}.kicker{font-size:11px;color:var(--blue);letter-spacing:1.8px;font-weight:800}.summary{color:var(--muted);line-height:1.8;font-size:16px;margin:0 0 22px;max-width:76ch}.objective-list{display:flex;gap:9px;list-style:none;padding:0;flex-wrap:wrap;margin:0 0 22px}.objective-list li{font-size:12px;line-height:1.6;padding:9px 12px;border:1px solid var(--line);border-radius:8px;background:var(--paper);color:var(--ink)}.resources{display:flex;flex-wrap:wrap;gap:10px;margin:23px 0 30px;font-size:13px}.resources a{border:1px solid var(--line);border-radius:8px;padding:9px 12px;text-decoration:none;font-weight:600}.resources a:hover{background:var(--soft)}
.tabs{display:flex;border-bottom:1px solid var(--line);gap:26px;margin-top:20px}.tab{background:none;border:0;padding:15px 2px;border-bottom:3px solid transparent;color:var(--muted);font-weight:650;font-size:14px}.tab[aria-selected=true]{color:var(--blue);border-bottom-color:var(--blue)}.panel{padding:24px 0 8px}.chapter{display:grid;grid-template-columns:66px 1fr;gap:18px;border:1px solid var(--line);border-radius:12px;padding:19px;margin-bottom:12px;background:var(--white)}.chapter button{border:1px solid var(--line);background:var(--soft);padding:9px 5px;border-radius:7px;color:var(--blue);font-size:12px;font-weight:700;height:36px}.chapter button:hover:not(:disabled){background:var(--blue);color:var(--white)}.chapter h3{font-size:17px;line-height:1.4;margin:3px 0 9px;font-weight:700}.chapter p{font-size:14px;color:var(--muted);line-height:1.75;margin:0 0 8px}.scene-text{margin:0 0 22px;padding:23px;border:1px solid var(--line);border-radius:12px;background:var(--white)}.scene-text h3{font-size:19px;margin:0 0 14px;line-height:1.45}.scene-text p{font-size:15px;line-height:1.85;color:var(--muted)}.scene-text pre{overflow:auto;background:var(--code);color:var(--code-text);padding:21px;border:1px solid var(--line);border-radius:10px;font:13px/1.8 Consolas,monospace;white-space:pre}.transcriptbar{display:flex;justify-content:space-between;gap:16px;align-items:center;margin-bottom:23px;padding:15px;background:var(--paper);border:1px solid var(--line);border-radius:10px}.transcriptbar p{font-size:13px;color:var(--muted);margin:0}.sources{padding-left:22px}.sources li{line-height:1.7;margin:0 0 17px}.notice{background:var(--soft);border:1px solid var(--line);border-left:3px solid var(--blue);border-radius:10px;padding:17px 18px;font-size:13px;line-height:1.8;margin-top:23px;color:var(--muted)}.notice b{display:block;margin-bottom:5px;color:var(--ink)}.footer{border-top:1px solid var(--line);background:var(--white);padding:23px 28px;text-align:center;font-size:12px;line-height:1.9;color:var(--muted)}[hidden]{display:none!important}.sr{position:absolute;left:-10000px;width:1px;height:1px;overflow:hidden}
@media(min-width:1150px){.sidebar{position:sticky;top:22px;align-self:start;max-height:calc(100vh - 44px);overflow:auto}}@media(max-width:1100px){.layout{grid-template-columns:275px minmax(0,1fr);gap:20px}.content{padding:20px}.headerline{display:block}.badge{margin-top:20px}.lesson{padding:12px 9px;gap:8px;grid-template-columns:29px 1fr}.lesson strong{font-size:13px}.number{font-size:12px;height:29px}.waiting p{font-size:13px}.chapter{padding:16px;gap:13px}}@media(max-width:780px){header{padding:27px 20px}.layout{display:flex;flex-direction:column;padding:22px 16px 42px}.sidebar{order:2;padding:20px 16px}.content{order:1;padding:18px}.lessonlist{display:grid;grid-template-columns:1fr 1fr}.controls{flex-wrap:wrap;margin-bottom:26px}.meta{width:100%;order:3;text-align:center}.tabs{gap:20px}.waiting p{display:none}.waiting strong{font-size:23px}.headerline h1{letter-spacing:-1px}.scene-text{padding:18px}.scene-text pre{padding:16px}.transcriptbar{align-items:flex-start;flex-direction:column}}@media(max-width:440px){.lessonlist{grid-template-columns:1fr}.chapter{grid-template-columns:54px 1fr;gap:11px;padding:14px}.resources{font-size:12px}.toplinks{gap:8px;font-size:12px}.toplinks a{padding:8px 10px}.content{padding:14px}.lessonhead h2{font-size:27px}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
</style></head><body>
<header><div class="brand">PLAYWRIGHT + IA / GUÍA DE CAMPO</div><div class="headerline"><div><h1>Del navegador al mainframe</h1><p>12 lecciones avanzadas con voz y subtítulos en inglés. TypeScript, Python y Java; servicios distribuidos y un terminal TN3270 de entrenamiento.</p></div><span class="badge" id="library-progress"></span></div>
<nav class="toplinks" aria-label="Material del curso"><a href="../CURSO-PLAYWRIGHT-IA.html">Curso de 2 horas</a><a href="LEEME-VIDEOS.md">Cómo usar los videos</a><a href="AI-PROMPTS-REGRESSION.md">Prompts de IA</a><a href="COURSE-VIDEO-MAP.md">Ruta de aprendizaje</a><a href="scripts/episodes.json">Guiones editables</a></nav></header>
<main class="layout"><aside class="sidebar"><h2>Lecciones</h2><label for="search" class="sr">Buscar lección</label><input class="search" id="search" type="search" placeholder="Buscar tema o lenguaje…" autocomplete="off"><nav class="lessonlist" id="lesson-list" aria-label="Elegir lección"></nav><p id="no-results" class="meta" hidden>No hay lecciones que coincidan.</p><div class="notice"><b>Complemento del taller</b>La serie sirve como preparación y repaso. Durante los 120 minutos en vivo, utiliza fragmentos y dedica el resto a practicar.</div></aside>
<section class="content" aria-label="Reproductor y material"><div class="screen"><video id="player" controls preload="metadata" playsinline aria-label="Video de la lección"></video><div id="waiting" class="waiting"><strong id="waiting-title"></strong><p id="waiting-description"></p></div></div>
<div class="controls"><button id="previous" type="button">← Anterior</button><span class="meta" id="video-meta"></span><button id="next" type="button">Siguiente →</button></div>
<div class="lessonhead"><div><div class="kicker" id="lesson-kicker"></div><h2 id="lesson-title" lang="en"></h2></div></div><p class="summary" id="lesson-summary" lang="en"></p><ul class="objective-list" id="objectives" lang="en"></ul>
<div class="resources" id="resources"></div><div class="tabs" role="tablist" aria-label="Material de la lección"><button type="button" role="tab" class="tab" id="tab-chapters" aria-controls="panel-chapters" aria-selected="true" tabindex="0">Pasos</button><button type="button" role="tab" class="tab" id="tab-transcript" aria-controls="panel-transcript" aria-selected="false" tabindex="-1">Guion y código</button><button type="button" role="tab" class="tab" id="tab-sources" aria-controls="panel-sources" aria-selected="false" tabindex="-1">Fuentes</button></div>
<section role="tabpanel" class="panel" id="panel-chapters" aria-labelledby="tab-chapters"></section><section role="tabpanel" class="panel" id="panel-transcript" aria-labelledby="tab-transcript" hidden></section><section role="tabpanel" class="panel" id="panel-sources" aria-labelledby="tab-sources" hidden></section>
<div class="notice"><b>Laboratorio local y datos sintéticos</b>Playwright automatiza el navegador y las API. IBM tnz se comunica con el terminal TN3270. El terminal incluido es un simulador; no es z/OS ni CICS y lee los datos de la aplicación de entrenamiento.</div>
</section></main><footer class="footer"><span id="footer-status"></span><br>Voz sintética de IA en inglés. Material de formación; sin relación con una aplicación real de HSBC.</footer><div id="announcer" class="sr" role="status" aria-live="polite"></div>
<script type="application/json" id="library-data">${data}</script>
<script>
const library = JSON.parse(document.getElementById('library-data').textContent);
const $ = id => document.getElementById(id);
const player = $('player');
const escape = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const format = seconds => { const value = Math.max(0, Math.floor(seconds)); return Math.floor(value / 60) + ':' + String(value % 60).padStart(2, '0'); };
let current = 0;
let captionURL;
let activeTab = 'chapters';
const key = 'playwright-video-library-progress-v1';
const progress = (() => { try { return JSON.parse(localStorage.getItem(key) || '{}'); } catch { return {}; } })();
const save = () => { try { localStorage.setItem(key, JSON.stringify(progress)); } catch {} };

function fullScript(lesson) {
  return lesson.id + '. ' + lesson.title + '\\n\\n' + lesson.scenes.map(scene => scene.title + '\\n\\n' + scene.narration +
    (scene.code ? '\\n\\n' + scene.code : '')).join('\\n\\n---\\n\\n');
}
function drawList() {
  const query = $('search').value.trim().toLowerCase();
  $('lesson-list').innerHTML = library.lessons.map((lesson, index) => {
    const visible = (lesson.title + ' ' + lesson.summary + ' ' + lesson.id).toLowerCase().includes(query);
    return '<button type="button" class="lesson" data-index="' + index + '" aria-current="' + (index === current) + '"' + (visible ? '' : ' hidden') + '><span class="number">' + lesson.id + '</span><span><strong lang="en">' + escape(lesson.title) + '</strong><small><i class="status-dot ' + (lesson.status === 'ready' ? 'ready' : '') + '"></i>' + escape(lesson.label) + (lesson.duration ? ' · ' + format(lesson.duration) : '') + (progress[lesson.id]?.completed ? ' · Visto' : '') + '</small></span></button>';
  }).join('');
  $('lesson-list').querySelectorAll('button').forEach(button => button.addEventListener('click', () => selectLesson(Number(button.dataset.index))));
  $('no-results').hidden = !!$('lesson-list').querySelector('button:not([hidden])');
}
function selectTab(name, focus = false) {
  activeTab = name;
  ['chapters', 'transcript', 'sources'].forEach(tab => {
    $('tab-' + tab).setAttribute('aria-selected', String(tab === name));
    $('tab-' + tab).tabIndex = tab === name ? 0 : -1;
    $('panel-' + tab).hidden = tab !== name;
  });
  if (focus) $('tab-' + name).focus();
}
function srtToVtt(srt) { return 'WEBVTT\\n\\n' + srt.replace(/\\r/g, '').replace(/(\\d{2}:\\d{2}:\\d{2}),(\\d{3})/g, '$1.$2'); }
function link(href, label, external = false) { return '<a href="' + escape(href) + '"' + (external ? ' target="_blank" rel="noopener noreferrer"' : '') + '>' + escape(label) + '</a>'; }
function selectLesson(index) {
  current = Math.max(0, Math.min(11, index));
  const lesson = library.lessons[current];
  player.pause(); player.removeAttribute('src'); player.replaceChildren(); player.load();
  if (captionURL) { URL.revokeObjectURL(captionURL); captionURL = undefined; }
  $('waiting').hidden = lesson.playable;
  $('waiting-title').textContent = lesson.label;
  $('waiting-description').textContent = lesson.status === 'pending'
    ? 'El video todavía no está terminado. El guion disponible puede consultarse debajo.'
    : 'El archivo todavía requiere revisión antes de presentarse como una lección terminada.';
  if (lesson.playable && lesson.render) {
    player.src = lesson.render;
    if (lesson.captions) {
      captionURL = URL.createObjectURL(new Blob([srtToVtt(lesson.captions)], { type: 'text/vtt' }));
      const track = document.createElement('track'); track.kind = 'subtitles'; track.label = 'English (optional text track)'; track.srclang = 'en'; track.default = false; track.src = captionURL; player.append(track);
    }
    player.load();
  }
  $('previous').disabled = current === 0; $('next').disabled = current === 11;
  $('video-meta').textContent = lesson.duration ? format(lesson.duration) + ' · English AI voice · ' + lesson.width + ' × ' + lesson.height : lesson.label;
  $('lesson-kicker').textContent = 'EPISODIO ' + lesson.id + ' / 12';
  $('lesson-title').textContent = lesson.title; $('lesson-summary').textContent = lesson.summary;
  $('objectives').innerHTML = lesson.objectives.map(text => '<li>' + escape(text) + '</li>').join('');
  $('resources').innerHTML = [lesson.render && lesson.playable ? link(lesson.render, 'Abrir MP4') : '', lesson.subtitles ? link(lesson.subtitles, 'Subtítulos SRT') : '', lesson.script ? link(lesson.script, 'Guion completo') : '', link('lab/distributed/README.md', 'Laboratorio distribuido'), link('lab/mainframe/README.md', 'Laboratorio TNZ')].filter(Boolean).join('');
  $('panel-chapters').innerHTML = lesson.scenes.length ? lesson.scenes.map((scene, i) => '<article class="chapter"><button type="button" data-scene="' + i + '" aria-label="Ir al paso ' + (i + 1) + ': ' + escape(scene.title) + '"' + (lesson.playable && scene.start !== null ? '' : ' disabled') + '>' + (scene.start !== null ? format(scene.start) : String(i + 1).padStart(2, '0')) + '</button><div lang="en"><h3>' + escape(scene.title) + '</h3>' + (scene.bullets || []).map(text => '<p>' + escape(text) + '</p>').join('') + '</div></article>').join('') : '<p class="meta">Los pasos aparecerán cuando esté terminado el guion de este episodio.</p>';
  $('panel-chapters').querySelectorAll('[data-scene]').forEach(button => button.addEventListener('click', () => { player.currentTime = lesson.scenes[Number(button.dataset.scene)].start; player.play().catch(() => {}); }));
  $('panel-transcript').innerHTML = '<div class="transcriptbar"><p>Texto de la narración y fragmentos de código en inglés.</p><button type="button" class="copy" id="copy-script"' + (lesson.scenes.length ? '' : ' disabled') + '>Copiar guion</button></div>' + lesson.scenes.map(scene => '<article class="scene-text" lang="en"><h3>' + escape(scene.title) + '</h3><p>' + escape(scene.narration).replace(/\\n/g, '<br>') + '</p>' + (scene.code ? '<pre><code>' + escape(scene.code) + '</code></pre>' : '') + '</article>').join('');
  $('copy-script').addEventListener('click', async () => {
    let copied = false;
    try { await navigator.clipboard.writeText(fullScript(lesson)); copied = true; } catch {
      const area = document.createElement('textarea'); area.value = fullScript(lesson); area.style.position = 'fixed'; area.style.opacity = '0'; document.body.append(area); area.select(); copied = document.execCommand('copy'); area.remove();
    }
    $('announcer').textContent = copied ? 'Guion copiado.' : 'No se pudo copiar. Selecciona el texto del guion para copiarlo manualmente.';
    $('copy-script').textContent = copied ? 'Copiado' : 'Selecciona el texto';
  });
  $('panel-sources').innerHTML = '<ul class="sources">' + lesson.sources.filter(source => /^https?:\\/\\//.test(source)).map(source => '<li>' + link(source, source.replace(/^https?:\\/\\//, ''), true) + '</li>').join('') + '</ul>' + '<p class="meta">Los enlaces abren la documentación original. Los fragmentos completos y las pruebas ejecutadas se encuentran en los laboratorios.</p>';
  selectTab(activeTab); drawList();
  try { history.replaceState(null, '', '#episode-' + lesson.id); } catch {}
  $('announcer').textContent = 'Episodio ' + lesson.id + ': ' + lesson.title;
}
$('previous').addEventListener('click', () => selectLesson(current - 1));
$('next').addEventListener('click', () => selectLesson(current + 1));
$('search').addEventListener('input', drawList);
['chapters', 'transcript', 'sources'].forEach((name, index, names) => {
  $('tab-' + name).addEventListener('click', () => selectTab(name));
  $('tab-' + name).addEventListener('keydown', event => {
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') { event.preventDefault(); selectTab(names[(index + (event.key === 'ArrowRight' ? 1 : 2)) % 3], true); }
    if (event.key === 'Home' || event.key === 'End') { event.preventDefault(); selectTab(names[event.key === 'Home' ? 0 : 2], true); }
  });
});
player.addEventListener('loadedmetadata', () => { const prior = progress[library.lessons[current].id]; if(prior && !prior.completed && prior.time > 2 && prior.time < player.duration - 5) player.currentTime = prior.time; });
player.addEventListener('timeupdate', () => { const id = library.lessons[current].id; if(!Number.isFinite(player.currentTime)) return; progress[id] = { ...progress[id], time: player.currentTime }; save(); });
player.addEventListener('ended', () => { const id = library.lessons[current].id; progress[id] = { time: 0, completed: true }; save(); drawList(); });
player.addEventListener('error', () => { if(!player.getAttribute('src')) return; $('waiting').hidden = false; $('waiting-title').textContent = 'No se pudo abrir el video'; $('waiting-description').textContent = 'Conserva la carpeta completa. Prueba Abrir MP4 o sirve la biblioteca desde la dirección local indicada en LEEME-VIDEOS.md.'; });
$('library-progress').textContent = library.ready + ' de 12 disponibles' + (library.ready ? ' · ' + Math.round(library.totalDuration / 60) + ' min' : '');
$('footer-status').innerHTML = (library.ready === 12 ? '12 archivos MP4 con imagen y audio verificados; duración de 6–8 minutos por episodio.' : 'Biblioteca en actualización. Cada video se habilita cuando su archivo y sus fuentes coinciden con la versión vigente.') + (library.finalQA ? ' ' + link(library.finalQA, 'Informe de revisión vigente') : ' Revisión audiovisual de la versión actual pendiente.');
const requested = location.hash.match(/^#episode-(\\d{2})$/)?.[1];
selectLesson(Math.max(0, library.lessons.findIndex(lesson => lesson.id === requested)));
</script></body></html>`;

writeFileSync(join(root, 'index.html'), html, 'utf8');
console.log(JSON.stringify({ generated: 'index.html', ffprobe: ffprobe || null, ready, expected: 12,
  totalVerifiedMinutes: Number((totalDuration / 60).toFixed(2)),
  lessons: lessons.map(({id,status,duration}) => ({id,status,duration})) }, null, 2));
if (strict && (ready !== 12 || lessons.some(lesson => !lesson.captions || !lesson.script || lesson.scenes.length === 0))) {
  console.error('Strict library validation failed: require all 12 playable 6–8 minute videos, subtitles, scripts and scenes.');
  process.exitCode = 1;
}

"""Validate or package the complete playable course. Default: read-only --dry-run.

Requires all 12 final MP4s and a current library marking all 12 available.
Run from videos: py -3.12 tools/package-full-course.py --create
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote
import zipfile

sys.dont_write_bytecode = True
VIDEO_ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = VIDEO_ROOT.parent
OUTPUT = VIDEO_ROOT / "delivery/Playwright-IA-curso-completo.zip"
PREFIX = "playwright-ai-course"
IDS = [f"{number:02}" for number in range(1, 13)]

spec = importlib.util.spec_from_file_location("course_sources", VIDEO_ROOT / "tools/package-course.py")
sources = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sources)

README = """# Empezar: Playwright avanzado con IA

Este paquete contiene los 12 videos MP4 finales con imagen 1080p y narración
sintética en inglés, subtítulos, guiones, prompts y código del curso de dos horas.
La serie completa sirve como preparación y repaso; el plan del taller indica
los fragmentos y ejercicios que se utilizan durante los 120 minutos de clase.

## Ver los videos

1. Extrae TODO el ZIP y conserva la carpeta playwright-ai-course y su estructura.
2. Abre videos/index.html en Edge u otro navegador actual. También puedes abrir
   directamente cualquiera de los 12 archivos en videos/renders.
3. Si el navegador limita archivos locales o quieres saltar entre capítulos,
   instala Node.js 22 o posterior. Desde la carpeta extraída playwright-ai-course,
   ejecuta en PowerShell:

   node videos/tools/serve-course.mjs

   Abre http://127.0.0.1:8766/videos/index.html. El servidor admite HTTP Range;
   mantén esa terminal abierta y usa Ctrl+C en ella para detenerlo.
   Si 8766 está ocupado: node videos/tools/serve-course.mjs --port 8768

Los MP4 incluyen la voz y subtítulos visibles. Los SRT separados y los tiempos de
escena están en videos/audio/01 a videos/audio/12. La biblioteca permite copiar
guiones y código. No necesita descargar los videos ni utilizar un servicio de IA
para reproducirlos después de extraer este ZIP.

## Preparar los laboratorios

Lee primero 01-PLAN-DEL-CURSO.md, 02-PROMPTS-COPIAR-PEGAR.md y los README de
videos/lab/distributed y videos/lab/mainframe. Instala Node.js, Python 3.12 y,
si eliges Java, JDK y Maven, según esas instrucciones. La instalación inicial de
paquetes y navegadores necesita internet. Este ZIP no instala esas herramientas
ni demuestra que ya funcionen en el equipo de quien lo recibe.

Cada participante ejecuta la aplicación distribuida y el simulador TN3270
localmente. IBM tnz es un cliente real; el servidor TN3270 es un simulador de
formación que consulta los mismos datos en memoria de TransferLab. No incluye
z/OS, CICS, DB2 ni acceso a un mainframe real. Los datos y capturas son sintéticos.
Los resúmenes de validación describen la estación de producción; ejecuta las
pruebas en tu equipo para obtener tus propios resultados.

## Editar y regenerar

Se incluyen fuentes Hyperframes, guiones, scripts de producción, recursos visuales
y dependencias fijadas en los manifiestos. No se incluyen paquetes instalados,
modelos de IA, cachés, trazas ni las pistas de voz WAV/MP3 separadas. La voz ya
mezclada en los MP4 sí está incluida para reproducción.

Para regenerar, instala las dependencias de videos/package-lock.json y
videos/tools/requirements-voice.txt y sigue videos/tools/AUDIO-ENGINE.md y
videos/qa/PRODUCTION.md. Regenera primero la narración con el motor configurado;
su servicio en línea recibe los guiones que elijas enviar. Los modelos Kokoro
son una alternativa opcional y se descargan por separado. Las composiciones
editables requieren que vuelvas a generar sus WAV antes de renderizar.
Las rutas absolutas de ejemplos de la estación original deben adaptarse al
lugar donde extrajiste este paquete.

COURSE-MANIFEST.json registra tamaños y SHA-256 de cada archivo de contenido,
incluido este README, y los controles técnicos de los 12 videos. El manifiesto
excluye únicamente su propio hash para evitar una dependencia circular.
Estos controles no sustituyen una revisión humana de la enseñanza o de la voz.
"""


def digest_file(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def json_file(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def executable(name, explicit):
    candidates = [explicit, os.environ.get(name.upper() + "_PATH"), shutil.which(name)]
    if os.environ.get("LOCALAPPDATA"):
        candidates.append(str(Path(os.environ["LOCALAPPDATA"]) / "Microsoft/WinGet/Links" / (name + ".exe")))
    for candidate in filter(None, candidates):
        try:
            completed = command(candidate, ["-version"], timeout=10)
            if completed.returncode == 0:
                return candidate
        except OSError:
            continue
    raise ValueError(f"{name} is required; install it or pass --{name} with its executable path.")


def command(program, args, timeout=300):
    return subprocess.run([str(program), *map(str, args)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)


class LibraryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("id") == "library-data":
            self.active = True
            self.blocks.append("")

    def handle_data(self, data):
        if self.active:
            self.blocks[-1] += data

    def handle_endtag(self, tag):
        if tag == "script":
            self.active = False


def expected_episodes():
    episodes = json_file(VIDEO_ROOT / "scripts/episodes.json")
    if not isinstance(episodes, list) or [entry.get("id") for entry in episodes] != IDS:
        raise ValueError("scripts/episodes.json must declare exactly episodes 01 through 12 in order.")
    if any(not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(entry.get("slug", ""))) for entry in episodes):
        raise ValueError("Episode slug is not a safe relative filename.")
    return episodes


def timeline_and_subtitles(episode):
    eid = episode["id"]
    folder = VIDEO_ROOT / "audio" / eid
    timeline = json_file(folder / "timeline.json")
    duration = float(timeline["duration"])
    if timeline.get("id") != eid or not math.isfinite(duration) or not 360 <= duration <= 480:
        raise ValueError(f"Episode {eid}: invalid timeline duration or ID.")
    if len(timeline.get("scenes", [])) != 12:
        raise ValueError(f"Episode {eid}: expected 12 timed scenes.")
    for source, timed in zip(episode["scenes"], timeline["scenes"], strict=True):
        if any(timed.get(key) != value for key, value in source.items()):
            raise ValueError(f"Episode {eid}: timeline is stale relative to the teaching script.")
    srt = (folder / "subtitles.srt").read_text(encoding="utf-8-sig")
    blocks = re.split(r"\n\s*\n", srt.strip())
    cues = timeline.get("captions", [])
    if not cues or len(blocks) != len(cues):
        raise ValueError(f"Episode {eid}: subtitle count differs from timeline.")
    previous = 0.0
    for number, (block, cue) in enumerate(zip(blocks, cues, strict=True), 1):
        lines = block.splitlines()
        match = re.fullmatch(r"(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})", lines[1]) if len(lines) >= 3 else None
        if not match or lines[0] != str(number):
            raise ValueError(f"Episode {eid}: malformed SRT cue {number}.")
        values = [int(value) for value in match.groups()]
        start = values[0] * 3600 + values[1] * 60 + values[2] + values[3] / 1000
        end = values[4] * 3600 + values[5] * 60 + values[6] + values[7] / 1000
        if not (previous - .002 <= start < end <= duration + .002):
            raise ValueError(f"Episode {eid}: subtitle cue {number} has invalid timing.")
        if (abs(start - cue["start"]) > .002 or abs(end - cue["end"]) > .002
                or "\n".join(lines[2:]) != cue["text"]):
            raise ValueError(f"Episode {eid}: subtitle cue {number} differs from timeline.")
        previous = end
    return timeline, srt


def inspect_video(path, duration, ffprobe, ffmpeg, decode):
    probed = command(ffprobe, ["-v", "error", "-show_format", "-show_streams", "-of", "json", path], timeout=30)
    if probed.returncode:
        raise ValueError(f"Cannot probe final video: {path.name}")
    info = json.loads(probed.stdout)
    actual = float(info.get("format", {}).get("duration", "nan"))
    video = next((item for item in info.get("streams", []) if item.get("codec_type") == "video"), {})
    audio = next((item for item in info.get("streams", []) if item.get("codec_type") == "audio"), {})
    if not math.isfinite(actual) or not 360 <= actual <= 480 or abs(actual - duration) > .3:
        raise ValueError(f"{path.name}: expected 6–8 minutes matching its narration.")
    if (video.get("width"), video.get("height"), video.get("codec_name")) != (1920, 1080, "h264"):
        raise ValueError(f"{path.name}: expected 1920x1080 H.264.")
    fps = float(Fraction(video.get("avg_frame_rate", "0/1")))
    if abs(fps - 24) > .001 or audio.get("codec_name") != "aac" or audio.get("channels", 0) < 1:
        raise ValueError(f"{path.name}: expected 24 fps and an AAC narration track.")
    if abs(float(audio.get("duration", "nan")) - duration) > .3 or not math.isfinite(float(audio.get("duration", "nan"))):
        raise ValueError(f"{path.name}: narration stream duration does not match timeline.")
    record = {"seconds": actual, "width": 1920, "height": 1080, "fps": fps,
              "videoCodec": "h264", "audioCodec": "aac", "audioDecode": "deferred until all 12 are available"}
    if decode:
        checked = command(ffmpeg, ["-hide_banner", "-nostdin", "-v", "info", "-i", path,
                                  "-map", "0:a:0", "-af", "volumedetect", "-f", "null", os.devnull])
        mean = re.search(r"mean_volume:\s*(-?[\d.]+) dB", checked.stderr)
        peak = re.search(r"max_volume:\s*(-?[\d.]+) dB", checked.stderr)
        if checked.returncode or not mean or not peak or float(mean.group(1)) < -50:
            raise ValueError(f"{path.name}: narration cannot be decoded or its signal is too quiet.")
        record.update(audioDecode="passed", meanVolumeDb=float(mean.group(1)), peakVolumeDb=float(peak.group(1)))
    return record


def verify_provenance(episode, path, progress):
    eid = episode["id"]
    record = progress.get("episodes", {}).get(eid, {})
    if record.get("stage") != "rendered":
        raise ValueError(f"Episode {eid}: no completed production checkpoint.")
    video_hash = digest_file(path)
    if record.get("artifact", {}).get("sha256") != video_hash:
        raise ValueError(f"Episode {eid}: MP4 differs from its production checkpoint.")
    validation = json_file(VIDEO_ROOT / "qa/episodes" / eid / "validation.json")
    if (validation.get("artifact", {}).get("sha256") != video_hash
            or validation.get("inputHash") != record.get("inputHash")):
        raise ValueError(f"Episode {eid}: validation report and production checkpoint disagree.")
    inputs = record.get("inputFiles", {})
    required = {f"audio/{eid}/timeline.json", f"audio/{eid}/subtitles.srt",
                f"audio/{eid}/narration.wav", "tools/build_compositions.py"}
    if not required.issubset(inputs):
        raise ValueError(f"Episode {eid}: checkpoint lacks required source hashes.")
    for relative, expected in inputs.items():
        source = VIDEO_ROOT / relative
        if source.is_symlink() or not sources.inside(source, VIDEO_ROOT.resolve()):
            raise ValueError(f"Episode {eid}: checkpoint source leaves the video workspace.")
        if not source.is_file() or digest_file(source) != expected:
            raise ValueError(f"Episode {eid}: source changed after render: {relative}; export it again.")
    return record["inputHash"], video_hash


def verify_final_qa(progress):
    report_path = VIDEO_ROOT / "qa/final-validation.json"
    report = json_file(report_path)
    palette = report.get("palette") or {}
    if (report.get("ready") is not True or report.get("verifiedEpisodes") != 12 or report.get("errors") != []
            or [item.get("episode") for item in report.get("videos", [])] != IDS
            or palette.get("currentFramesAudited") != 144 or palette.get("significantGreenRegions") != 0
            or palette.get("greenTealLiterals") != 0
            or palette.get("criteria", {}).get("minimumRegionAreaPixels") != 16
            or palette.get("status") != "passed_for_active_sources_and_sampled_frames"):
        raise ValueError("Final QA must approve all twelve current exports and the final 144-frame palette audit.")
    if palette.get("sha256") != digest_file(VIDEO_ROOT / "qa/blue-palette-validation.json"):
        raise ValueError("Final QA refers to a different palette report; finalize the current audit again.")
    if report.get("reviewMarkdownSha256") != digest_file(VIDEO_ROOT / "qa/VIDEO-REVIEW.md"):
        raise ValueError("Final QA Markdown and JSON are not the same validated pair.")
    for item in report["videos"]:
        record = progress.get("episodes", {}).get(item["episode"], {})
        if item.get("sha256") != record.get("artifact", {}).get("sha256") or item.get("inputHash") != record.get("inputHash"):
            raise ValueError(f"Final QA is stale for episode {item['episode']}.")
    evidence = report.get("evidenceSha256", {})
    if not evidence:
        raise ValueError("Final QA has no verifiable evidence hashes.")
    for relative, expected in evidence.items():
        path = VIDEO_ROOT / relative
        if path.is_symlink() or not sources.inside(path, WORK_ROOT.resolve()):
            raise ValueError("Final QA evidence leaves the course workspace.")
        if not path.is_file() or digest_file(path) != expected:
            raise ValueError(f"Final QA evidence changed: {relative}; run the final audit/finalizer again.")


def check_ready(episodes, ffprobe, ffmpeg):
    errors, media = [], []
    parser = LibraryParser()
    library_path = VIDEO_ROOT / "index.html"
    if library_path.is_file():
        parser.feed(library_path.read_text(encoding="utf-8-sig"))
    if len(parser.blocks) != 1:
        library = {}
        errors.append("videos/index.html is missing its single library-data JSON block.")
    else:
        library = json.loads(parser.blocks[0])
    lessons = library.get("lessons", [])
    if library.get("ready") != 12 or [item.get("id") for item in lessons] != IDS:
        errors.append("The library must contain exactly episodes 01–12 and ready=12; regenerate it with --strict after rendering.")
    by_id = {item.get("id"): item for item in lessons}
    progress_path = VIDEO_ROOT / "production-progress.json"
    progress = json_file(progress_path) if progress_path.is_file() else {}
    try:
        verify_final_qa(progress)
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append(f"Final QA: {error}")
    paths = [VIDEO_ROOT / "renders" / f"{ep['id']}-{ep['slug']}.mp4" for ep in episodes]
    all_exist = all(path.is_file() and path.stat().st_size > 0 for path in paths)
    decode = all_exist and library.get("ready") == 12
    for episode, path in zip(episodes, paths, strict=True):
        eid = episode["id"]
        if not path.is_file() or not path.stat().st_size:
            errors.append(f"Episode {eid}: final MP4 is missing.")
            continue
        try:
            if path.is_symlink() or not sources.inside(path, WORK_ROOT):
                raise ValueError(f"Episode {eid}: MP4 leaves the course workspace.")
            timeline, srt = timeline_and_subtitles(episode)
            lesson = by_id.get(eid, {})
            expected_render = path.relative_to(VIDEO_ROOT).as_posix()
            expected_script = f"compositions/{eid}-{episode['slug']}/SCRIPT.md"
            if (lesson.get("status") != "ready" or lesson.get("playable") is not True
                    or unquote(lesson.get("render") or "") != expected_render
                    or unquote(lesson.get("subtitles") or "") != f"audio/{eid}/subtitles.srt"
                    or unquote(lesson.get("script") or "") != expected_script
                    or (lesson.get("captions") or "").replace("\r\n", "\n") != srt):
                raise ValueError(f"Episode {eid}: library availability, links or subtitles are stale.")
            if (VIDEO_ROOT / expected_script).read_text(encoding="utf-8-sig") != "\n\n".join(s["narration"] for s in episode["scenes"]):
                raise ValueError(f"Episode {eid}: composition SCRIPT.md is stale.")
            if len(lesson.get("scenes", [])) != 12:
                raise ValueError(f"Episode {eid}: library needs 12 chapter markers.")
            for timed, linked in zip(timeline["scenes"], lesson["scenes"], strict=True):
                if any(linked.get(key) != value for key, value in episode["scenes"][int(timed['id'][-2:]) - 1].items()) or linked.get("start") != timed["start"]:
                    raise ValueError(f"Episode {eid}: library scene content or chapter timing is stale.")
            input_hash, video_hash = verify_provenance(episode, path, progress)
            facts = inspect_video(path, timeline["duration"], ffprobe, ffmpeg, decode)
            if abs(float(lesson.get("duration", 0)) - facts["seconds"]) > .001:
                raise ValueError(f"Episode {eid}: library duration does not match the MP4.")
            media.append({"episode": eid, "path": path.relative_to(WORK_ROOT).as_posix(),
                          "inputHash": input_hash, "sha256": video_hash, **facts})
        except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
            errors.append(str(error))
    if len(media) == 12 and abs(float(library.get("totalDuration", 0)) - sum(item["seconds"] for item in media)) > .01:
        errors.append("Library total duration does not match the twelve final MP4 files.")
    return errors, media, paths


def selected_sources():
    paths = set(sources.source_files(include_subtitles=True))
    # Diagnostic voice/calibration measurements are not course lessons.
    paths = {path for path in paths if path != VIDEO_ROOT / "qa/edge-voice-sample.json"
             and not any(part in {"00", "98"} for part in path.relative_to(WORK_ROOT).parts)}
    paths.add(VIDEO_ROOT / "index.html")
    # These exact synthetic classroom assets are needed by the editable builder;
    # no request dumps, browser storage, traces or recorded test videos are added.
    captures = list((VIDEO_ROOT / "lab/distributed/evidence/test-results").glob("regression-TR-01-*/ui-success.png"))
    if len(captures) != 1:
        raise ValueError("Require exactly one synthetic TR-01 screenshot used by the builder.")
    extras = [captures[0], VIDEO_ROOT / "lab/mainframe/evidence/hybrid-python-browser.png",
              VIDEO_ROOT / "lab/mainframe/evidence/hybrid-python-terminal.txt"]
    extras.extend((VIDEO_ROOT / "compositions").glob("02-*/assets/evidence-02-06.png"))
    extras.extend((VIDEO_ROOT / "compositions").glob("11-*/assets/evidence-11-10.png"))
    for path in extras:
        if not path.is_file():
            raise ValueError(f"Required synthetic teaching asset missing: {path.relative_to(WORK_ROOT)}")
        if path.suffix == ".png" and path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Invalid PNG teaching asset: {path.name}")
        paths.add(path)
    return sorted(paths, key=lambda path: path.relative_to(WORK_ROOT).as_posix())


def write_zip(output, records, manifest, overwrite=False, guards=None):
    if output.exists() and not overwrite:
        raise FileExistsError("The exact delivery ZIP already exists; pass --overwrite to replace it.")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".building")
    if temporary.exists():
        raise FileExistsError("A .building package exists. Inspect that exact file before retrying.")
    with zipfile.ZipFile(temporary, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
        archive.writestr(f"{PREFIX}/README-EMPEZAR.md", README.encode("utf-8"))
        for record in records:
            path = WORK_ROOT / record["path"]
            mode = zipfile.ZIP_STORED if path.suffix.lower() == ".mp4" else zipfile.ZIP_DEFLATED
            info = zipfile.ZipInfo(f"{PREFIX}/{record['path']}")
            info.compress_type = mode
            checksum = hashlib.sha256()
            size = 0
            with path.open("rb") as source, archive.open(info, "w", force_zip64=True) as target:
                while chunk := source.read(1024 * 1024):
                    checksum.update(chunk)
                    size += len(chunk)
                    target.write(chunk)
            if checksum.hexdigest() != record["sha256"] or size != record["bytes"]:
                raise RuntimeError(f"Source changed during packaging: {record['path']}; staged ZIP preserved.")
        archive.writestr(f"{PREFIX}/COURSE-MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"))
    with zipfile.ZipFile(temporary) as archive:
        damaged = archive.testzip()
        if damaged:
            raise RuntimeError(f"ZIP CRC validation failed: {damaged}")
        for record in manifest["files"]:
            with archive.open(f"{PREFIX}/{record['path']}") as member:
                if hashlib.file_digest(member, "sha256").hexdigest() != record["sha256"]:
                    raise RuntimeError(f"ZIP SHA-256 validation failed: {record['path']}")
        if sum(item.filename.endswith(".mp4") for item in archive.infolist()) != 12:
            raise RuntimeError("Complete package must contain exactly 12 MP4 files.")
    # A producer/editor may have changed a source after it was copied. Do not publish
    # a package whose file versions no longer match the validated snapshot.
    for record in records:
        if digest_file(WORK_ROOT / record["path"]) != record["sha256"]:
            raise RuntimeError(f"Source changed before promotion: {record['path']}; staged ZIP preserved.")
    for path, expected in (guards or {}).items():
        if not path.is_file() or digest_file(path) != expected:
            raise RuntimeError(f"Production input changed before promotion: {path.name}; staged ZIP preserved.")
    if output.exists() and not overwrite:
        raise FileExistsError("A delivery ZIP appeared during packaging; staged ZIP preserved.")
    os.replace(temporary, output)
    return {"zipBytes": output.stat().st_size, "zipSha256": digest_file(output), "testzip": "passed", "memberSha256": "passed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--dry-run", action="store_true", help="Read-only validation and inventory; default")
    action.add_argument("--create", action="store_true", help="Create the complete ZIP after all gates pass")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing only the fixed complete-course ZIP")
    parser.add_argument("--ffprobe", help="FFprobe executable")
    parser.add_argument("--ffmpeg", help="FFmpeg executable")
    args = parser.parse_args()
    output = OUTPUT.resolve()
    if not sources.inside(output, WORK_ROOT.resolve()) or output.suffix != ".zip" or OUTPUT.is_symlink():
        raise ValueError("Delivery output must stay inside this course workspace.")
    episodes = expected_episodes()
    ffprobe, ffmpeg = executable("ffprobe", args.ffprobe), executable("ffmpeg", args.ffmpeg)
    source_paths = selected_sources()
    records = sources.build_inventory(source_paths)
    videos = [VIDEO_ROOT / "renders" / f"{episode['id']}-{episode['slug']}.mp4" for episode in episodes]
    for path in videos:
        if path.is_file():
            records.append({"path": path.relative_to(WORK_ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": digest_file(path)})
    # Snapshot provenance dependencies that are verified but deliberately not archived.
    guarded_paths = {VIDEO_ROOT / "production-progress.json"}
    progress_path = VIDEO_ROOT / "production-progress.json"
    if progress_path.is_file():
        for record in json_file(progress_path).get("episodes", {}).values():
            for relative in record.get("inputFiles", {}):
                source = VIDEO_ROOT / relative
                if not sources.inside(source, VIDEO_ROOT.resolve()) or source.is_symlink():
                    raise ValueError("A provenance dependency leaves the video workspace.")
                guarded_paths.add(source)
    guards = {path: digest_file(path) for path in guarded_paths if path.is_file()}
    errors, media, videos = check_ready(episodes, ffprobe, ffmpeg)
    for record in records:
        if digest_file(WORK_ROOT / record["path"]) != record["sha256"]:
            errors.append(f"Content changed during validation: {record['path']}; retry after editing/rendering finishes.")
    for path, expected in guards.items():
        if not path.is_file() or digest_file(path) != expected:
            errors.append(f"Production input changed during validation: {path.name}; retry after rendering finishes.")
    required_materials = sources.TOP_LEVEL_FILES | {"videos/LEEME-VIDEOS.md", "videos/COURSE-VIDEO-MAP.md",
        "videos/AI-PROMPTS-REGRESSION.md", "videos/FRAGMENTOS-PARA-LA-CLASE.md", "videos/tools/serve-course.mjs"}
    missing_materials = required_materials - {record["path"] for record in records}
    if missing_materials:
        errors.append("Required teaching material is missing: " + ", ".join(sorted(missing_materials)))
    records.sort(key=lambda item: item["path"])
    summary = {"mode": "create" if args.create else "dry-run", "ready": not errors,
               "expectedVideos": 12, "presentFinalVideos": sum(path.is_file() for path in videos),
               "validatedVideos": len(media), "contentFiles": len(records) + 1,
               "contentBytes": sum(item["bytes"] for item in records) + len(README.encode("utf-8")),
               "output": str(output), "errors": errors, "videos": media,
               "containsInstalledDependencies": False, "containsModelWeights": False,
               "containsSeparateVoiceTracks": False, "containsTraces": False,
               "compression": {"mp4": "STORE", "other": "DEFLATE"}, "written": False}
    if errors or not args.create:
        print(json.dumps(summary, ensure_ascii=True, indent=2))
        return 2 if errors else 0
    readme_record = {"path": "README-EMPEZAR.md", "bytes": len(README.encode("utf-8")), "sha256": hashlib.sha256(README.encode("utf-8")).hexdigest()}
    manifest = {"generatedAt": datetime.now(timezone.utc).isoformat(), "packageType": "complete-playable-course",
                "files": [readme_record, *records], "videos": media,
                "excluded": sorted(sources.EXCLUDED_DIRECTORIES - {"renders", "evidence"}),
                "excludedMedia": ["separate WAV/MP3 voice tracks", "calibration MP4s", "test recordings", "traces"],
                "evidenceScope": "Only selected synthetic screenshots, a terminal excerpt and textual summaries; no traces.",
                "verificationScope": "Technical file, media, audio-signal and library validation; no listening or ASR claim.",
                "manifestSelfHash": "Excluded to avoid circular hashing."}
    summary.update(write_zip(output, records, manifest, overwrite=args.overwrite, guards=guards), written=True)
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, IndexError, subprocess.TimeoutExpired) as error:
        print(f"Complete-course packaging stopped: {error}", file=sys.stderr)
        sys.exit(1)

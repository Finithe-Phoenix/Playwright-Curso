"""Checkpointed Hyperframes production for the twelve narrated course episodes.

Use --plan to inspect readiness without creating files or starting a render.
Full production is sequential; an incomplete audio set exits 2 unless --wait is used.
"""
from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
BUILDER = ROOT / "tools/build_compositions.py"
CLI = ROOT / "node_modules/hyperframes/dist/cli.js"
PROGRESS = ROOT / "production-progress.json"
LOCK = ROOT / ".production.lock"
DEFAULT_BROWSER = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE = {"hyperframes": "0.8.33", "width": 1920, "height": 1080, "fps": 24,
           "quality": "high", "workers": 1, "lowMemoryMode": True, "gpu": True,
           "staticFrameDedup": True, "durationToleranceSeconds": 0.3}
EPISODES = [f"{number:02}" for number in range(1, 13)]
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def utc():
    return datetime.now(timezone.utc).isoformat()


def emit(stage, episode=None, **details):
    print(json.dumps({"time": utc(), "episode": episode, "stage": stage, **details}, ensure_ascii=False), flush=True)


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def atomic_json(path, data):
    path = Path(path).resolve()
    path.relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pid_alive(pid):
    if not isinstance(pid, int) or pid <= 0:
        return False
    if os.name == "nt":
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return ctypes.get_last_error() == 5  # Access denied is not proof the owner exited.
        try:
            code = wintypes.DWORD()
            return bool(kernel.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == 259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


class ProductionLock:
    def __enter__(self):
        if LOCK.exists():
            previous = read_json(LOCK)
            if previous.get("owner") != "render_course" or pid_alive(previous.get("pid")):
                raise RuntimeError("Another production process owns .production.lock; do not run two batches together.")
            LOCK.resolve().relative_to(ROOT)
            LOCK.unlink()
        descriptor = os.open(LOCK, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump({"owner": "render_course", "pid": os.getpid(), "startedAt": utc()}, handle)
        return self

    def __exit__(self, *_):
        if LOCK.exists() and read_json(LOCK).get("pid") == os.getpid():
            LOCK.unlink()


def stop_owned_process(process, log):
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       stdout=log, stderr=subprocess.STDOUT, timeout=20,
                       creationflags=subprocess.CREATE_NO_WINDOW, check=False)
    else:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
    process.wait(timeout=20)


def run_command(command, episode, stage, timeout, environment, *, json_output=False):
    log_path = ROOT / "logs" / f"{episode}-{stage}.{'json' if json_output else 'log'}"
    error_path = ROOT / "logs" / f"{episode}-{stage}.stderr.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    emit(stage, episode, log=relative(log_path))
    started = time.monotonic()
    flags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    with log_path.open("w", encoding="utf-8") as output:
        error = error_path.open("w", encoding="utf-8") if json_output else None
        try:
            process = subprocess.Popen([str(value) for value in command], cwd=ROOT, env=environment,
                                       stdout=output, stderr=error or subprocess.STDOUT,
                                       creationflags=flags, start_new_session=os.name != "nt")
            last_notice = started
            try:
                while process.poll() is None:
                    elapsed = time.monotonic() - started
                    if elapsed >= timeout:
                        raise TimeoutError(f"{episode} {stage} exceeded {timeout} seconds; see {relative(log_path)}")
                    if time.monotonic() - last_notice >= 30:
                        emit(stage, episode, elapsedSeconds=round(elapsed), log=relative(log_path))
                        last_notice = time.monotonic()
                    time.sleep(0.5)
            except BaseException:
                stop_owned_process(process, output)
                raise
            if process.returncode:
                raise RuntimeError(f"{episode} {stage} exited {process.returncode}; see {relative(log_path)}")
        finally:
            if error:
                error.close()
    result = {"log": relative(log_path), "seconds": round(time.monotonic() - started, 3)}
    if json_output:
        raw = ANSI.sub("", log_path.read_text(encoding="utf-8-sig")).strip()
        try:
            report = json.loads(raw)
        except json.JSONDecodeError:
            report = None
            for found in re.finditer(r"\{", raw):
                try:
                    candidate, _ = json.JSONDecoder().raw_decode(raw[found.start():])
                    if isinstance(candidate, dict) and "ok" in candidate:
                        report = candidate
                        break
                except json.JSONDecodeError:
                    continue
            if report is None:
                raise RuntimeError(f"No structured Hyperframes check result in {relative(log_path)}")
        if not isinstance(report, dict) or report.get("ok") is not True:
            raise RuntimeError(f"Hyperframes check reported ok=false for {episode}; see {relative(log_path)}")
        result.update(ok=True, stderr=relative(error_path))
    return result


def ffprobe(path, executable):
    result = subprocess.run([executable, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                            capture_output=True, text=True, encoding="utf-8", timeout=30, check=False,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    if result.returncode:
        raise ValueError(f"FFprobe cannot validate {relative(path)}: {result.stderr.strip()[:400]}")
    return json.loads(result.stdout)


def finite(value, label):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def validate_timeline(timeline, episode):
    if timeline.get("id") != episode:
        raise ValueError(f"Timeline episode mismatch: requested {episode}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(timeline.get("slug", ""))):
        raise ValueError("Timeline slug is not a safe filename")
    duration = finite(timeline.get("duration"), "Episode duration")
    if not 360 <= duration <= 480:
        raise ValueError(f"Episode {episode} is {duration:.3f}s; the required duration is 360–480s. Regenerate narration deliberately.")
    scenes = timeline.get("scenes", [])
    if len(scenes) != 12:
        raise ValueError(f"Episode {episode} must contain 12 timed scenes")
    end = 0.0
    for number, scene in enumerate(scenes, 1):
        if scene.get("id") != f"{episode}-{number:02}":
            raise ValueError("Scene IDs must be consecutive within their episode")
        start, length = finite(scene.get("start"), "Scene start"), finite(scene.get("duration"), "Scene duration")
        if length <= 0 or abs(start - end) > 0.03:
            raise ValueError(f"Scene {scene['id']} has a gap, overlap, or invalid duration")
        end = start + length
    if abs(end - duration) > 0.03:
        raise ValueError("Scene endpoints do not match the narration timeline")
    captions = timeline.get("captions", [])
    if not captions:
        raise ValueError("Narration timeline has no captions")
    previous_end = 0.0
    for number, cue in enumerate(captions, 1):
        start, end = finite(cue.get("start"), "Caption start"), finite(cue.get("end"), "Caption end")
        if start < -0.001 or end <= start or end > duration + 0.03 or start < previous_end - 0.02:
            raise ValueError(f"Caption {number} is out of bounds, overlapping, or empty")
        if not str(cue.get("text", "")).strip():
            raise ValueError(f"Caption {number} has no text")
        previous_end = end
    return duration


def subtitle_seconds(value):
    hours, minutes, tail = value.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(tail)


def validate_srt(path, timeline):
    raw = path.read_text(encoding="utf-8-sig")
    matches = re.findall(r"(\d{2}:\d{2}:\d{2}[,.]\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2}[,.]\d{3})", raw)
    if len(matches) != len(timeline["captions"]):
        raise ValueError("SRT and timeline have different caption counts; wait for completed synthesis or regenerate subtitles")
    for number, ((start, end), cue) in enumerate(zip(matches, timeline["captions"], strict=True), 1):
        if abs(subtitle_seconds(start) - cue["start"]) > 0.002 or abs(subtitle_seconds(end) - cue["end"]) > 0.002:
            raise ValueError(f"SRT cue {number} does not match the actual narration timing")


def validate_media(path, expected_duration, probe, *, narrated_video=True):
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Missing or empty media: {relative(path)}")
    info = ffprobe(path, probe)
    duration = finite(info.get("format", {}).get("duration"), "Media duration")
    if abs(duration - expected_duration) > PROFILE["durationToleranceSeconds"]:
        raise ValueError(f"{relative(path)} lasts {duration:.3f}s; narration lasts {expected_duration:.3f}s")
    audio = next((stream for stream in info.get("streams", []) if stream.get("codec_type") == "audio"), None)
    if not audio or int(audio.get("channels", 0)) <= 0:
        raise ValueError(f"No usable audio stream in {relative(path)}")
    result = {"duration": duration, "audioCodec": audio.get("codec_name"), "audioChannels": audio.get("channels"),
              "sampleRate": audio.get("sample_rate"), "bytes": path.stat().st_size}
    if narrated_video:
        video = next((stream for stream in info.get("streams", []) if stream.get("codec_type") == "video"), None)
        if not video or video.get("codec_name") != "h264" or (video.get("width"), video.get("height")) != (1920, 1080):
            raise ValueError("Render must contain H.264 video at exactly 1920×1080")
        fps = float(Fraction(video.get("avg_frame_rate") or video.get("r_frame_rate") or "0/1"))
        if abs(fps - 24) > 0.001:
            raise ValueError(f"Render frame rate must be 24 fps, observed {fps}")
        if audio.get("duration") is not None and abs(float(audio["duration"]) - expected_duration) > 0.3:
            raise ValueError("Rendered audio duration does not match narration")
        result.update(width=1920, height=1080, fps=fps, videoCodec="h264", sha256=file_hash(path))
    return result


def inputs_for(episode, probe):
    folder = ROOT / "audio" / episode
    timeline_path, narration, subtitles = folder / "timeline.json", folder / "narration.wav", folder / "subtitles.srt"
    if not all(path.is_file() and path.stat().st_size for path in (timeline_path, narration, subtitles)):
        return None
    timeline = read_json(timeline_path)
    duration = validate_timeline(timeline, episode)
    validate_srt(subtitles, timeline)
    narration_info = validate_media(narration, duration, probe, narrated_video=False)
    dependencies = [timeline_path, BUILDER, narration, subtitles,
                    *[ROOT / "assets" / name for name in ("gsap.min.js", "SourceSans3.ttf", "JetBrainsMono.ttf")]]
    if episode == "02":
        proof = next((ROOT / "lab/distributed/evidence/test-results").glob("regression-TR-01-*/ui-success.png"), None)
        if proof is None:
            raise ValueError("Episode 02 needs the actual successful UI screenshot")
        dependencies.append(proof)
    if episode == "11":
        dependencies.extend(ROOT / "lab/mainframe/evidence" / name for name in ("hybrid-python-browser.png", "hybrid-python-terminal.txt"))
    hashes = {relative(path): file_hash(path) for path in dependencies}
    digest = hashlib.sha256(json.dumps({"files": hashes, "profile": PROFILE}, sort_keys=True).encode()).hexdigest()
    name = f"{episode}-{timeline['slug']}"
    return {"episode": episode, "timeline": timeline, "duration": duration, "inputHash": digest,
            "inputFiles": hashes, "narration": narration_info, "name": name,
            "project": ROOT / "compositions" / name, "output": ROOT / "renders" / f"{name}.mp4"}


def environment_for(browser, verification_budget_ms=90000):
    environment = os.environ.copy()
    environment.update(HYPERFRAMES_BROWSER_PATH=browser, HF_STATIC_DEDUP="true", HF_STATIC_DEDUP_VERIFY="true",
                       HF_COURSE_STATIC_VERIFY_MAX_MS=str(verification_budget_ms),
                       PRODUCER_LOW_MEMORY_MODE="true", PRODUCER_MAX_WORKERS="1",
                       PRODUCER_ENABLE_STREAMING_ENCODE="true",
                       PRODUCER_STREAMING_ENCODE_MAX_DURATION_SECONDS="600", PYTHONUNBUFFERED="1")
    return environment


class Producer:
    def __init__(self, args, node, probe, encoder, environment):
        self.args, self.node, self.probe, self.encoder, self.environment = args, node, probe, encoder, environment
        self.progress = read_json(PROGRESS) if PROGRESS.exists() else {"schemaVersion": 1, "episodes": {}}
        if self.progress.get("schemaVersion") != 1:
            raise ValueError("Unknown production-progress.json version; preserve it before migrating")
        self.progress["profile"] = PROFILE

    def stage(self, episode, stage, **details):
        record = self.progress["episodes"].setdefault(episode, {})
        record.update(stage=stage, updatedAt=utc(), **details)
        self.progress["updatedAt"] = utc()
        atomic_json(PROGRESS, self.progress)
        return record

    def produce(self, data):
        episode, digest, output = data["episode"], data["inputHash"], data["output"]
        old = dict(self.progress["episodes"].get(episode, {}))
        if output.is_file() and old.get("inputHash") == digest and old.get("artifact"):
            validated = validate_media(output, data["duration"], self.probe)
            if validated["sha256"] != old["artifact"].get("sha256"):
                raise ValueError(f"Episode {episode} output changed outside its checkpoint; preserving it for review")
            self.stage(episode, "rendered", artifact={**old["artifact"], "path": relative(output), **validated}, reused=True)
            emit("reused", episode, output=relative(output), duration=validated["duration"])
            return
        if output.is_file() and not old.get("inputHash") and not self.args.adopt_existing:
            raise ValueError(f"Existing untracked {relative(output)} is preserved. Use --adopt-existing only after reviewing its provenance.")
        adopt_existing = bool(output.is_file() and self.args.adopt_existing and
                              (not old.get("inputHash") or old.get("pendingAdoption")))
        self.stage(episode, "input_validated", inputHash=digest, inputFiles=data["inputFiles"],
                   narration=data["narration"], expectedDuration=data["duration"],
                   voice={key: data["timeline"].get(key) for key in ("engine", "voice", "rate")},
                   previousArtifact=old.get("artifact") or old.get("previousArtifact"), artifact=None,
                   pendingAdoption=adopt_existing, reused=False, error=None)
        project = data["project"]
        self.stage(episode, "building")
        build = run_command([PYTHON, BUILDER, "--episode", episode], episode, "build", 300, self.environment)
        if not (project / "index.html").is_file():
            raise RuntimeError(f"Builder did not create episode {episode}")
        midpoint_values = [scene["start"] + scene["duration"] / 2 for scene in data["timeline"]["scenes"]]
        midpoints = ",".join(f"{value:.5f}" for value in midpoint_values)
        self.stage(episode, "checking", build=build)
        check = run_command([self.node, CLI, "check", project, "--json", f"--at={midpoints}", "--timeout=20000"],
                            episode, "check", 300, self.environment, json_output=True)
        self.stage(episode, "snapshotting", check=check)
        snapshot_folder = ROOT / "qa/episodes" / episode / digest[:12]
        snapshots = run_command([self.node, CLI, "snapshot", project, f"--at={midpoints}", "--no-end", "--describe=false",
                                 "--timeout=20000", f"--output={snapshot_folder}"], episode, "snapshots", 300, self.environment)
        frames = sorted(snapshot_folder.glob("*.png"))
        sheets = sorted(snapshot_folder.glob("contact-sheet*.jpg"))
        if len(frames) != 12 or not sheets:
            raise RuntimeError(f"Episode {episode} needs 12 midpoint PNGs and a contact sheet, found {len(frames)} PNGs/{len(sheets)} sheets")
        snapshots.update(frames=[relative(path) for path in frames], contactSheets=[relative(path) for path in sheets],
                         times=midpoint_values, visualReview="pending")
        self.stage(episode, "rendering", snapshots=snapshots)
        staged = ROOT / "renders/.staging" / f"{data['name']}-{digest[:16]}.mp4"
        staged.parent.mkdir(parents=True, exist_ok=True)
        source = output if adopt_existing else staged
        render = {"adopted": source == output}
        if source == staged:
            staged_valid = False
            if staged.is_file():
                try:
                    validate_media(staged, data["duration"], self.probe)
                    staged_valid = True
                except (ValueError, subprocess.SubprocessError):
                    # Keep incomplete output as evidence; the next attempt gets a new staging filename.
                    staged = staged.with_name(staged.stem + f"-retry-{int(time.time())}.mp4")
                    source = staged
            if not staged_valid:
                render = run_command([self.node, CLI, "render", project, f"--output={staged}", "--fps=24", "--quality=high",
                                      "--workers=1", "--low-memory-mode", "--gpu", "--quiet", "--no-best-effort"],
                                     episode, "render", self.args.render_timeout, self.environment)
            else:
                render = {"recoveredStagingFile": relative(staged)}
        self.stage(episode, "validating", render=render)
        artifact = validate_media(source, data["duration"], self.probe)
        if not self.args.skip_audio_check:
            audio = run_command([self.encoder, "-hide_banner", "-nostats", "-v", "error", "-xerror", "-i", source,
                                 "-map", "0:a:0", "-f", "null", os.devnull], episode, "audio-integrity", 300, self.environment)
            artifact["audioDecode"] = {"ok": True, **audio}
        if self.args.audio_metrics:
            metrics = run_command([self.encoder, "-hide_banner", "-nostats", "-i", source, "-vn", "-af",
                                   "astats=metadata=1:reset=0", "-f", "null", os.devnull], episode, "audio-metrics", 300, self.environment)
            text = (ROOT / metrics["log"]).read_text(encoding="utf-8", errors="replace")
            for label, key in (("Peak level dB", "peakDb"), ("RMS level dB", "rmsDb")):
                values = re.findall(re.escape(label) + r":\s*(-?\d+(?:\.\d+)?|-?inf)", text)
                if not values or not math.isfinite(float(values[-1])):
                    raise ValueError("Audio level analysis found silence or unavailable metrics")
                metrics[key] = float(values[-1])
            artifact["audioMetrics"] = metrics
        # Re-read inputs before promotion. A concurrent source edit invalidates this render.
        latest = inputs_for(episode, self.probe)
        if latest is None or latest["inputHash"] != digest:
            raise ValueError(f"Episode {episode} inputs changed during production; staged render is preserved")
        if source != output:
            output.parent.mkdir(parents=True, exist_ok=True)
            source.resolve().relative_to(ROOT)
            output.resolve().relative_to(ROOT)
            os.replace(source, output)
        atomic_json(ROOT / "qa/episodes" / episode / "validation.json", {
            "episode": episode, "inputHash": digest, "profile": PROFILE, "artifact": {"path": relative(output), **artifact},
            "check": check, "captions": {"count": len(data["timeline"]["captions"]), "bounds": "passed", "srtMatchesTimeline": True},
            "snapshots": snapshots, "visualReview": "pending", "validatedAt": utc(),
        })
        self.stage(episode, "rendered", artifact={"path": relative(output), **artifact}, pendingAdoption=False, visualReview="pending")
        emit("rendered", episode, output=relative(output), duration=round(artifact["duration"], 3),
             contactSheets=snapshots["contactSheets"], visualReview="pending")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--episode", choices=EPISODES)
    selection.add_argument("--all", action="store_true", help="Process episodes 01–12; this is the default")
    selection.add_argument("--from-episode", "--from", dest="from_episode", choices=EPISODES,
                           help="Process this episode and the remaining episodes, for example --from 02")
    inspection = parser.add_mutually_exclusive_group()
    inspection.add_argument("--plan", action="store_true", help="Read-only readiness inspection, no build or render")
    inspection.add_argument("--verify-only", action="store_true", help="Read-only media validation; does not adopt files or claim check/visual approval")
    parser.add_argument("--wait", type=float, default=0, metavar="SECONDS", help="Maximum accumulated idle wait for missing audio, default 0")
    parser.add_argument("--render-timeout", type=int, default=1800)
    parser.add_argument("--browser", default=os.environ.get("HYPERFRAMES_BROWSER_PATH", DEFAULT_BROWSER))
    parser.add_argument("--ffprobe", default=shutil.which("ffprobe"))
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg"))
    parser.add_argument("--skip-audio-check", action="store_true", help="Skip full audio decoding; stream presence is still mandatory")
    parser.add_argument("--audio-metrics", action="store_true", help="Also decode peak and RMS statistics")
    parser.add_argument("--adopt-existing", action="store_true", help="Adopt an untracked MP4 only after operator review of its provenance")
    parser.add_argument("--verification-budget-ms", type=int, default=90000,
                        help="Time budget for verified static-frame reuse, default 90000; frame comparisons remain enabled")
    args = parser.parse_args()
    if not math.isfinite(args.wait) or args.wait < 0 or args.render_timeout <= 0:
        raise ValueError("Wait must be finite and nonnegative; render timeout must be positive")
    if not 15000 <= args.verification_budget_ms <= 300000:
        raise ValueError("Verification budget must be between 15000 and 300000 ms")
    selected = [args.episode] if args.episode else [episode for episode in EPISODES if episode >= (args.from_episode or "01")]
    if not args.ffprobe:
        raise ValueError("FFprobe is required; put it in PATH or use --ffprobe")
    if args.plan:
        statuses = []
        for episode in selected:
            data = inputs_for(episode, args.ffprobe)
            statuses.append({"episode": episode, "audioReady": data is not None,
                             "duration": data["duration"] if data else None,
                             "inputHash": data["inputHash"] if data else None})
        emit("plan", episodes=statuses, buildsStarted=0, rendersStarted=0)
        return 0
    if args.verify_only:
        for episode in selected:
            data = inputs_for(episode, args.ffprobe)
            if data is None:
                raise ValueError(f"Episode {episode} narration is not ready")
            artifact = validate_media(data["output"], data["duration"], args.ffprobe)
            emit("media_verified", episode, output=relative(data["output"]), artifact=artifact,
                 inputHash=data["inputHash"], provenance="not adopted", check="not evaluated", visualReview="not evaluated")
        return 0
    node = shutil.which("node")
    if not node or not PYTHON.is_file() or not CLI.is_file() or not Path(args.browser).is_file():
        raise ValueError("Require Node, videos/.venv Python, installed Hyperframes CLI, and the configured Chrome executable")
    if read_json(ROOT / "node_modules/hyperframes/package.json").get("version") != "0.8.33":
        raise ValueError("This production profile was verified with Hyperframes 0.8.33")
    if not args.ffmpeg and (not args.skip_audio_check or args.audio_metrics):
        raise ValueError("FFmpeg is required for audio decoding; put it in PATH or use --ffmpeg")
    environment = environment_for(args.browser, args.verification_budget_ms)
    with ProductionLock():
        from configure_hyperframes import configure
        performance = configure(args.verification_budget_ms)
        producer = Producer(args, node, args.ffprobe, args.ffmpeg, environment)
        producer.progress["performance"] = performance
        pending = list(selected)
        idle = 0.0
        while pending:
            progressed = False
            for episode in list(pending):
                try:
                    data = inputs_for(episode, args.ffprobe)
                    if data is None:
                        producer.stage(episode, "waiting_for_audio")
                        continue
                    producer.produce(data)
                    pending.remove(episode)
                    progressed = True
                except BaseException as error:
                    producer.stage(episode, "interrupted" if isinstance(error, KeyboardInterrupt) else "failed", error=str(error))
                    raise
            if pending and not progressed:
                if idle >= args.wait:
                    emit("incomplete", pending=pending, idleWaitSeconds=round(idle), progressFile=relative(PROGRESS))
                    return 2
                pause = min(15.0, args.wait - idle)
                emit("waiting_for_audio", pending=pending, idleWaitSeconds=round(idle), nextCheckSeconds=pause)
                time.sleep(pause)
                idle += pause
        emit("selected_batch_rendered", episodes=selected, visualReview="pending", progressFile=relative(PROGRESS))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        emit("interrupted", message="Stopped the owned child process; completed MP4s and checkpoints are preserved")
        sys.exit(130)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        emit("failed", message=str(error))
        sys.exit(1)

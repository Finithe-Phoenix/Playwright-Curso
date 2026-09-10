"""Extract reproducible scene midpoint samples from completed course MP4 exports.

Run with videos/.venv/Scripts/python.exe tools/review_exports.py --episode 01
or --available. Requires ffmpeg, ffprobe and Pillow (validated with 11.3.0).
This tool creates review material; it never claims that visual review occurred.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

from PIL import Image, ImageDraw, ImageFont


VIDEOS = Path(__file__).resolve().parents[1]
TOOL_VERSION = "1.0.0"
FRAME_SIZE = (1920, 1080)
TILE_SIZE = (640, 360)
LABEL_HEIGHT = 24


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value) -> None:
    temporary = path.with_suffix(".tmp.json")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")
    os.replace(temporary, path)


def relative(path: Path) -> str:
    return path.relative_to(VIDEOS).as_posix()


def run(arguments: list[str]) -> str:
    result = subprocess.run(arguments, check=False, capture_output=True,
                            text=True, encoding="utf-8", errors="replace",
                            timeout=180)
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): "
                           f"{arguments[0]}\n{result.stderr[-5000:]}")
    return result.stdout


def probe(path: Path, executable: str) -> dict:
    result = json.loads(run([executable, "-v", "error", "-show_streams",
                             "-show_format", "-of", "json", str(path)]))
    streams = result.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not video or not audio:
        raise ValueError("A completed episode must contain video and audio streams.")
    duration = float(result["format"]["duration"])
    if duration <= 0:
        raise ValueError("The export has no positive duration.")
    return {
        "durationSeconds": duration,
        "videoCodec": video.get("codec_name"),
        "width": video.get("width"),
        "height": video.get("height"),
        "averageFrameRate": video.get("avg_frame_rate"),
        "audioCodec": audio.get("codec_name"),
        "audioChannels": audio.get("channels"),
        "withinRequestedSixToEightMinutes": 360 <= duration <= 480,
        "native1920x1080": (video.get("width"), video.get("height")) == FRAME_SIZE,
    }


def timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    minutes, remainder = divmod(milliseconds, 60_000)
    whole_seconds, fraction = divmod(remainder, 1000)
    return f"{minutes:02}:{whole_seconds:02}.{fraction:03}"


def label_font():
    fonts = [Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/arial.ttf",
             Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]
    for font in fonts:
        if font.is_file():
            return ImageFont.truetype(str(font), 17)
    return ImageFont.load_default(size=17)


def contact_sheet(frames: list[dict], directory: Path, number: int) -> dict:
    sheet = Image.new("RGB", (1920, 768), "#101522")
    draw = ImageDraw.Draw(sheet)
    font = label_font()
    for index, frame in enumerate(frames):
        x = (index % 3) * TILE_SIZE[0]
        y = (index // 3) * (TILE_SIZE[1] + LABEL_HEIGHT)
        with Image.open(directory / frame["file"]) as original:
            tile = original.convert("RGB").resize(TILE_SIZE, Image.Resampling.LANCZOS)
            sheet.paste(tile, (x, y))
        label = f'{frame["sceneId"]} | {frame["timestamp"]} | {frame["title"]}'
        while draw.textbbox((0, 0), label, font=font)[2] > 626:
            label = label[:-4] + "..."
        draw.text((x + 7, y + TILE_SIZE[1] + 2), label, fill="white", font=font)
    name = f"contact-{number:02}.jpg"
    destination = directory / name
    temporary = directory / f"contact-{number:02}.tmp.jpg"
    sheet.save(temporary, quality=94, subsampling=0)
    os.replace(temporary, destination)
    return {"file": name, "width": 1920, "height": 768,
            "sceneIds": [f["sceneId"] for f in frames], "sha256": sha256(destination)}


def valid_cache(manifest: dict, directory: Path, mp4_hash: str,
                timeline_hash: str) -> bool:
    if (manifest.get("toolVersion") != TOOL_VERSION
            or manifest.get("input", {}).get("sha256") != mp4_hash
            or manifest.get("timeline", {}).get("sha256") != timeline_hash):
        return False
    outputs = manifest.get("frames", []) + manifest.get("contactSheets", [])
    if len(manifest.get("frames", [])) != 12 or len(outputs) != 14:
        return False
    return all((directory / item["file"]).is_file()
               and sha256(directory / item["file"]) == item["sha256"]
               for item in outputs)


def review_material(episode: dict, ffmpeg: str, ffprobe: str,
                    require_final: bool = False) -> dict:
    episode_id = episode["id"]
    movie = VIDEOS / "renders" / f'{episode_id}-{episode["slug"]}.mp4'
    timeline_path = VIDEOS / "audio" / episode_id / "timeline.json"
    if not movie.is_file():
        raise FileNotFoundError(f"Completed episode export is absent: {movie}")
    if not timeline_path.is_file():
        raise FileNotFoundError(f"Actual narration timeline is absent: {timeline_path}")
    initial_stat = movie.stat()
    mp4_hash, timeline_hash = sha256(movie), sha256(timeline_path)
    production_state = None
    if require_final:
        progress = load_json(VIDEOS / "production-progress.json")
        record = progress.get("episodes", {}).get(episode_id, {})
        recorded_timeline = record.get("inputFiles", {}).get(relative(timeline_path))
        artifact = record.get("artifact") or {}
        if (record.get("stage") != "rendered" or recorded_timeline != timeline_hash
                or artifact.get("sha256") != mp4_hash
                or artifact.get("path") != relative(movie)):
            raise ValueError("Export is not final for the current timeline: require "
                             "stage=rendered and matching timeline/artifact SHA-256.")
        production_state = {"checkedAtUtc": utc_now(), "stage": "rendered",
                            "timelineSha256": timeline_hash,
                            "artifactSha256": mp4_hash,
                            "matchesCurrentTimelineAndArtifact": True}
    directory = VIDEOS / "qa" / "export-review" / episode_id
    directory.mkdir(parents=True, exist_ok=True)
    manifest_path = directory / "manifest.json"
    if manifest_path.is_file():
        manifest = load_json(manifest_path)
        if valid_cache(manifest, directory, mp4_hash, timeline_hash):
            if production_state:
                manifest["productionState"] = production_state
                write_json(manifest_path, manifest)
            return {"episode": episode_id, "status": "cached",
                    "manifest": relative(manifest_path), "sha256": mp4_hash,
                    "sampleCount": 12, "contactSheetCount": 2}
    metadata = probe(movie, ffprobe)
    timeline = load_json(timeline_path)
    scenes = timeline.get("scenes", [])
    if timeline.get("id") != episode_id or len(scenes) != 12:
        raise ValueError("Timeline must belong to this episode and have exactly 12 scenes.")
    expected_ids = [f"{episode_id}-{number:02}" for number in range(1, 13)]
    if [s["id"] for s in scenes] != expected_ids:
        raise ValueError("Timeline scene identifiers are missing, duplicated or out of order.")
    samples = []
    for scene in scenes:
        start, duration = float(scene["start"]), float(scene["duration"])
        midpoint = start + duration / 2
        if start < 0 or duration <= 0 or not 0 <= midpoint < metadata["durationSeconds"]:
            raise ValueError(f'Invalid midpoint for scene {scene["id"]}.')
        name = f'{scene["id"]}-midpoint.png'
        destination = directory / name
        temporary = directory / f'{scene["id"]}-midpoint.tmp.png'
        # -ss before -i uses accurate seek with re-encoding; default accurate seek
        # decodes and discards frames up to this real timeline timestamp.
        run([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
             "-ss", f"{midpoint:.6f}", "-i", str(movie), "-map", "0:v:0",
             "-frames:v", "1", "-vf",
             "scale=1920:1080:force_original_aspect_ratio=decrease,"
             "pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
             "-threads", "1", str(temporary)])
        os.replace(temporary, destination)
        samples.append({"sceneId": scene["id"], "title": scene["title"],
                        "sceneStartSeconds": start, "sceneDurationSeconds": duration,
                        "sampleSeconds": round(midpoint, 6),
                        "timestamp": timestamp(midpoint), "file": name,
                        "width": 1920, "height": 1080, "sha256": sha256(destination)})
    contacts = [contact_sheet(samples[:6], directory, 1),
                contact_sheet(samples[6:], directory, 2)]
    final_stat = movie.stat()
    if (initial_stat.st_size, initial_stat.st_mtime_ns) != (
            final_stat.st_size, final_stat.st_mtime_ns):
        raise RuntimeError("The MP4 changed during sampling. Rerun after export completes.")
    manifest = {
        "schemaVersion": 1, "toolVersion": TOOL_VERSION, "createdAtUtc": utc_now(),
        "episode": episode_id, "title": episode["title"],
        "input": {"file": relative(movie), "sha256": mp4_hash,
                  "sizeBytes": final_stat.st_size,
                  "modifiedAtUtc": datetime.fromtimestamp(
                      final_stat.st_mtime, timezone.utc).isoformat()},
        "timeline": {"file": relative(timeline_path), "sha256": timeline_hash,
                     "sampling": "One frame at start + duration / 2 for each actual scene"},
        "mediaProbe": metadata, "frames": samples, "contactSheets": contacts,
        "visualReviewPerformedByAgent": False,
        "visualReview": None,
        "productionState": production_state,
        "scope": "Technical extraction only. Samples do not establish full playback, "
                 "animation continuity, subtitle synchronization or audio quality. "
                 "Any subsequent visual observations must identify this MP4 SHA-256.",
    }
    write_json(manifest_path, manifest)
    return {"episode": episode_id, "status": "extracted",
            "manifest": relative(manifest_path), "sha256": mp4_hash,
            "sampleCount": len(samples), "contactSheetCount": len(contacts),
            "durationSeconds": metadata["durationSeconds"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--episode", help="Completed course episode number, 01 through 12")
    choice.add_argument("--available", action="store_true",
                        help="Sample exact registered course exports that already exist")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--require-final", action="store_true",
                        help="Require rendered production stage and matching current hashes")
    arguments = parser.parse_args()
    for name in (arguments.ffmpeg, arguments.ffprobe):
        if shutil.which(name) is None:
            parser.error(f"Executable is unavailable: {name}")
    episodes = load_json(VIDEOS / "scripts" / "episodes.json")
    registry = {e["id"]: e for e in episodes if e["id"] in
                {f"{number:02}" for number in range(1, 13)}}
    if arguments.episode is not None:
        try:
            requested = f"{int(arguments.episode):02}"
        except ValueError:
            parser.error("--episode must be a number from 01 through 12.")
        if requested not in registry:
            parser.error("--episode must select a registered episode from 01 through 12.")
        selected = [registry[requested]]
    else:
        selected = [episode for _, episode in sorted(registry.items())
                    if (VIDEOS / "renders" /
                        f'{episode["id"]}-{episode["slug"]}.mp4').is_file()]
    failures = 0
    for episode in selected:
        try:
            result = review_material(episode, arguments.ffmpeg, arguments.ffprobe,
                                     arguments.require_final)
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
            failures += 1
            result = {"episode": episode["id"], "status": "error", "error": str(error)}
        print(json.dumps(result, ensure_ascii=False), flush=True)
    print(json.dumps({"completedExportsSelected": len(selected), "errors": failures,
                      "calibrationExportsExcluded": True,
                      "automaticVisualApproval": False}), flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

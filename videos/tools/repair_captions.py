"""Repair completed episode captions from saved provider boundaries without synthesizing audio.

Examples: --episode 05; --episode 01 --episode 02; --all
Only the active narration variant's cache metadata is updated. Other audio variants
and every WAV/MP3 remain untouched; media SHA-256 hashes are verified before/after.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import soundfile as sf

from synthesize_edge import LEAD, ROOT, atomic_json, caption_units, group_captions, speech_plan, timestamp

REVISION = 2
EXACT_ALIGNMENT = "original words aligned to provider boundaries"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def media_hashes(folder):
    result = {}
    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".wav", ".mp3"}:
            with path.open("rb") as stream:
                result[path.relative_to(ROOT).as_posix()] = hashlib.file_digest(stream, "sha256").hexdigest()
    return result


def validate_cues(cues, duration, label):
    previous = -1.0
    for cue in cues:
        start, end = cue["start"], cue["end"]
        if not (math.isfinite(start) and math.isfinite(end) and 0 <= start < end <= duration):
            raise ValueError(f"{label}: caption outside audio")
        if start < previous - 0.001 or not cue["text"].strip():
            raise ValueError(f"{label}: empty, overlapping, or unordered caption")
        previous = end


def stage_episode(episode):
    eid = episode["id"]
    folder = ROOT / "audio" / eid
    timeline_path = folder / "timeline.json"
    timeline = read_json(timeline_path)
    if len(timeline["scenes"]) != len(episode["scenes"]):
        raise ValueError(f"{eid}: scene count differs from current script")
    info = sf.info(folder / "narration.wav")
    if abs(info.duration - timeline["duration"]) >= 1 / info.samplerate:
        raise ValueError(f"{eid}: narration and timeline durations differ")
    updates, captions, cursor, changed_scenes, words = [], [], 0.0, [], 0
    for scene, recorded in zip(episode["scenes"], timeline["scenes"]):
        sid = scene["id"]
        if any(recorded.get(key) != value for key, value in scene.items()):
            raise ValueError(f"{sid}: timeline differs from current script")
        metadata_path = folder / (sid + ".json")
        metadata = read_json(metadata_path)
        digest = hashlib.sha256(json.dumps({"narration": scene["narration"], "voice": timeline["voice"],
            "rate": timeline["rate"], "engine": timeline["engine"], "captionVersion": 1}, sort_keys=True).encode()).hexdigest()
        if metadata["hash"] != digest:
            raise ValueError(f"{sid}: audio hash does not match the current narration")
        scene_info = sf.info(ROOT / recorded["audio"])
        if (abs(recorded["start"] - cursor) >= 1 / info.samplerate
                or abs(scene_info.duration - recorded["duration"]) >= 1 / info.samplerate
                or abs(metadata["duration"] - recorded["duration"]) >= 1 / info.samplerate):
            raise ValueError(f"{sid}: scene timing differs from audio")
        original, spoken, spans = speech_plan(scene["narration"])
        if spoken != metadata["spoken_text"]:
            raise ValueError(f"{sid}: pronunciation plan differs from saved narration")
        units, alignment = caption_units(original, spoken, spans, metadata["word_boundaries"])
        cues = group_captions(units)
        if alignment != EXACT_ALIGNMENT or " ".join(cue["text"] for cue in cues) != " ".join(original):
            raise ValueError(f"{sid}: exact source-word restoration was not possible")
        validate_cues(cues, metadata["duration"], sid)
        starts = {LEAD + boundary["offset"] / 1e7 for boundary in metadata["word_boundaries"]}
        ends = {LEAD + (boundary["offset"] + boundary["duration"]) / 1e7
                for boundary in metadata["word_boundaries"]}
        if any(cue["start"] not in starts or cue["end"] not in ends for cue in cues):
            raise ValueError(f"{sid}: caption boundaries were not supplied by the provider")
        if metadata["cues"] != cues or metadata["caption_alignment"] != alignment:
            changed_scenes.append(sid)
        repaired = {**metadata, "cues": cues, "caption_alignment": alignment, "caption_mapping_revision": REVISION}
        updates.append((metadata_path, repaired))
        cache_path = folder / ".cache" / (sid + "-" + digest[:16] + ".json")
        cached = read_json(cache_path)
        for field in ("hash", "duration", "voice", "rate", "engine", "spoken_text", "word_boundaries"):
            if cached[field] != metadata[field]:
                raise ValueError(f"{sid}: active cache differs in {field}")
        updates.append((cache_path, {**cached, "cues": cues, "caption_alignment": alignment,
                                    "caption_mapping_revision": REVISION}))
        captions.extend({**cue, "start": cue["start"] + cursor, "end": cue["end"] + cursor} for cue in cues)
        words += len(original)
        cursor += recorded["duration"]
    if abs(cursor - timeline["duration"]) >= 1 / info.samplerate:
        raise ValueError(f"{eid}: scene total differs from narration")
    validate_cues(captions, timeline["duration"], eid)
    repaired_timeline = {**timeline, "captions": captions, "caption_mapping_revision": REVISION}
    updates.append((timeline_path, repaired_timeline))
    srt = "\n\n".join(f"{index + 1}\n{timestamp(cue['start'])} --> {timestamp(cue['end'])}\n{cue['text']}"
                         for index, cue in enumerate(captions)) + "\n"
    return {"folder": folder, "updates": updates, "srt": srt, "before_media": media_hashes(folder),
            "summary": {"episode": eid, "scenes": len(episode["scenes"]), "source_words": words,
                        "captions": len(captions), "caption_content_changed_scenes": changed_scenes,
                        "caption_mapping_revision": REVISION, "seconds": timeline["duration"]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--episode", action="append", help="Completed episode ID; may be repeated")
    choice.add_argument("--all", action="store_true", help="Repair every completed episode in the current script")
    args = parser.parse_args()
    episodes = read_json(ROOT / "scripts/episodes.json")
    if isinstance(episodes, dict):
        episodes = episodes["episodes"]
    available = {episode["id"] for episode in episodes}
    if args.episode and set(args.episode) - available:
        parser.error("Unknown episode: " + ", ".join(sorted(set(args.episode) - available)))
    selected, skipped = [], []
    for episode in episodes:
        eid = episode["id"]
        if args.episode and eid not in args.episode:
            continue
        folder = ROOT / "audio" / eid
        required = [folder / "timeline.json", folder / "narration.wav"]
        required.extend(folder / (scene["id"] + ".json") for scene in episode["scenes"])
        if not all(path.is_file() for path in required):
            if args.episode:
                raise ValueError(f"{eid}: narration generation is incomplete")
            skipped.append(eid)
            continue
        selected.append(episode)
    if not selected:
        raise ValueError("No completed episodes selected")
    # Validate every requested episode before replacing any metadata.
    staged = [stage_episode(episode) for episode in selected]
    summaries = []
    for item in staged:
        folder = item["folder"]
        if media_hashes(folder) != item["before_media"]:
            raise RuntimeError(f"{folder.name}: audio changed during validation; stop the producer before repair")
        for path, payload in item["updates"]:
            if read_json(path) != payload:
                atomic_json(path, payload)
        srt_path = folder / "subtitles.srt"
        if not srt_path.exists() or srt_path.read_text(encoding="utf-8") != item["srt"]:
            temporary = srt_path.with_suffix(".srt.tmp")
            temporary.write_text(item["srt"], encoding="utf-8")
            temporary.replace(srt_path)
        after_media = media_hashes(folder)
        if after_media != item["before_media"]:
            raise RuntimeError(f"{folder.name}: media SHA-256 changed unexpectedly")
        for path, payload in item["updates"]:
            if read_json(path) != payload:
                raise RuntimeError(f"{path}: persisted metadata verification failed")
        if srt_path.read_text(encoding="utf-8") != item["srt"]:
            raise RuntimeError(f"{srt_path}: persisted SRT verification failed")
        summaries.append({**item["summary"], "media_files_verified_unchanged": len(after_media),
            "wav_files_verified_unchanged": sum(path.endswith(".wav") for path in after_media),
            "media_sha256_manifest": hashlib.sha256(json.dumps(after_media, sort_keys=True).encode()).hexdigest()})
    print(json.dumps({"repaired_episodes": len(summaries), "episodes": summaries, "skipped_incomplete": skipped,
        "audio_synthesis_performed": False, "scope": "Exact source text and saved provider timing; no listening or ASR claim"}, indent=2))


if __name__ == "__main__":
    main()

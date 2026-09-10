"""Checkpointed English neural narration with actual provider word timestamps."""
from __future__ import annotations

import argparse
import asyncio
from bisect import bisect_right
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import re
import shutil
import time

import edge_tts
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
RATE = 24000
LEAD, TAIL = 0.6, 0.65
ENGINE = "edge-tts " + version("edge-tts")
EXPANSIONS = {"TN3270": "T N thirty two seventy", "TNZ": "T N Z", "JUnit": "J Unit", "pytest": "pie test",
              "API": "A P I", "UI": "U I", "CI": "C I", "DB2": "D B two", "z/OS": "zee O S", "JSON": "J S O N"}


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def normalized(text):
    return "".join(character.lower() for character in text if character.isalnum())


def speech_plan(text):
    original = text.replace("`", "").split()
    spoken_words, spans, cursor = [], [], 0
    for token in original:
        pronounced = token
        for source, replacement in EXPANSIONS.items():
            pronounced = re.sub(r"\b" + re.escape(source) + r"\b", replacement, pronounced)
        spoken_words.append(pronounced)
        spans.append((cursor, cursor + len(normalized(pronounced))))
        cursor = spans[-1][1]
    return original, " ".join(spoken_words), spans


def caption_units(original, spoken, spans, boundaries):
    """Restore original words while retaining exact provider spans, including multiword spans."""
    def provider_units():
        return [{"text": item["text"], "start": LEAD + item["offset"] / 1e7,
                 "end": LEAD + (item["offset"] + item["duration"]) / 1e7}
                for item in boundaries], "provider words"

    stream = normalized(spoken)
    starts = [start for start, _ in spans]
    cursor, mapped = 0, []
    for boundary in boundaries:
        token = normalized(boundary["text"])
        location = stream.find(token, cursor) if token else -1
        if location != cursor:
            # Do not restore words if the provider omitted or changed any spoken text.
            return provider_units()
        first = max(0, bisect_right(starts, location) - 1)
        last = max(first, bisect_right(starts, location + len(token) - 1) - 1)
        begin, end = LEAD + boundary["offset"] / 1e7, LEAD + (boundary["offset"] + boundary["duration"]) / 1e7
        if mapped and first <= mapped[-1]["last"]:
            # Acronym letters and partially shared words belong to one timed unit.
            mapped[-1]["last"] = max(mapped[-1]["last"], last)
            mapped[-1]["end"] = max(mapped[-1]["end"], end)
        else:
            expected = mapped[-1]["last"] + 1 if mapped else 0
            if first != expected:
                return provider_units()
            mapped.append({"first": first, "last": last, "start": begin, "end": end})
        cursor = location + len(token)
    if cursor != len(stream) or not mapped or mapped[-1]["last"] != len(original) - 1:
        return provider_units()
    return [{"text": " ".join(original[item["first"]:item["last"] + 1]),
             "start": item["start"], "end": item["end"]} for item in mapped], "original words aligned to provider boundaries"


def group_captions(units):
    cues, group = [], []
    for unit in units:
        if group and (len(" ".join(item["text"] for item in group + [unit])) > 86 or unit["end"] - group[0]["start"] > 7):
            cues.append({"text": " ".join(item["text"] for item in group), "start": group[0]["start"], "end": group[-1]["end"]})
            group = []
        group.append(unit)
    if group:
        cues.append({"text": " ".join(item["text"] for item in group), "start": group[0]["start"], "end": group[-1]["end"]})
    return cues


def timestamp(seconds):
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


async def synthesize_scene(scene, folder, voice, rate):
    digest = hashlib.sha256(json.dumps({"narration": scene["narration"], "voice": voice, "rate": rate,
                                      "engine": ENGINE, "captionVersion": 1}, sort_keys=True).encode()).hexdigest()
    cache = folder / ".cache"
    cache.mkdir(exist_ok=True)
    stem = scene["id"] + "-" + digest[:16]
    cached_wav, cached_meta, cached_mp3 = (cache / (stem + suffix) for suffix in (".wav", ".json", ".mp3"))
    if cached_wav.exists() and cached_meta.exists():
        metadata = json.loads(cached_meta.read_text(encoding="utf-8"))
        if metadata.get("hash") == digest:
            print("AUDIO_REUSED " + scene["id"], flush=True)
            shutil.copyfile(cached_wav, folder / (scene["id"] + ".wav"))
            atomic_json(folder / (scene["id"] + ".json"), metadata)
            return metadata
    original, spoken, spans = speech_plan(scene["narration"])
    started, boundaries = time.monotonic(), []
    part = cached_mp3.with_suffix(".mp3.part")
    for attempt in range(3):
        boundaries = []
        try:
            communicator = edge_tts.Communicate(spoken, voice=voice, rate=rate, boundary="WordBoundary",
                                               connect_timeout=15, receive_timeout=60)
            with part.open("wb") as stream:
                async for event in communicator.stream():
                    if event["type"] == "audio":
                        stream.write(event["data"])
                    elif event["type"] == "WordBoundary":
                        boundaries.append(event)
            if not part.stat().st_size or not boundaries:
                raise RuntimeError("Provider returned no audio or no word boundaries")
            part.replace(cached_mp3)
            break
        except Exception:
            if attempt == 2:
                raise
            await asyncio.sleep(2 ** (attempt + 1))
    audio, sample_rate = sf.read(cached_mp3, dtype="float32")
    if sample_rate != RATE or audio.ndim != 1 or not len(audio) or not np.isfinite(audio).all():
        raise RuntimeError(f"Unexpected or invalid audio format for {scene['id']}: {sample_rate}")
    units, alignment = caption_units(original, spoken, spans, boundaries)
    cues = group_captions(units)
    speech_duration = len(audio) / RATE
    audio = np.concatenate([np.zeros(round(LEAD * RATE), dtype=np.float32), audio,
                            np.zeros(round(TAIL * RATE), dtype=np.float32)])
    if cues and cues[-1]["end"] > LEAD + speech_duration + 0.1:
        raise RuntimeError("Provider timestamps exceed decoded audio")
    peak = float(np.max(np.abs(audio)))
    if peak > .94:
        audio *= .94 / peak
    temporary_wav = cached_wav.with_suffix(".wav.part")
    sf.write(temporary_wav, audio, RATE, format="WAV", subtype="PCM_16")
    temporary_wav.replace(cached_wav)
    metadata = {"hash": digest, "duration": len(audio) / RATE, "cues": cues, "word_boundaries": boundaries,
                "caption_alignment": alignment, "peak": float(np.max(np.abs(audio))), "voice": voice, "rate": rate,
                "engine": ENGINE, "generation_seconds": time.monotonic() - started,
                "original_words": len(original), "spoken_words": len(spoken.split()), "spoken_text": spoken}
    atomic_json(cached_meta, metadata)
    shutil.copyfile(cached_wav, folder / (scene["id"] + ".wav"))
    atomic_json(folder / (scene["id"] + ".json"), metadata)
    print(json.dumps({"scene": scene["id"], "seconds": round(metadata["duration"], 2),
                      "generation_seconds": round(metadata["generation_seconds"], 2), "status": "narrated"}), flush=True)
    return metadata


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode")
    parser.add_argument("--from-episode", help="Start at this two-digit episode ID, preserving earlier episodes")
    parser.add_argument("--rate", default="+0%")
    parser.add_argument("--voice", default="en-US-JennyNeural")
    args = parser.parse_args()
    episodes = json.loads((ROOT / "scripts/episodes.json").read_text(encoding="utf-8"))
    if isinstance(episodes, dict):
        episodes = episodes["episodes"]
    selected = [episode for episode in episodes if (not args.episode or episode["id"] == args.episode)
                and (not args.from_episode or episode["id"] >= args.from_episode)]
    if not selected:
        raise ValueError("No episode matches " + str(args.episode))
    for episode in selected:
        started = time.monotonic()
        folder = ROOT / "audio" / episode["id"]
        folder.mkdir(parents=True, exist_ok=True)
        scenes, captions, cursor = [], [], 0.0
        for scene in episode["scenes"]:
            metadata = await synthesize_scene(scene, folder, args.voice, args.rate)
            scenes.append({**scene, "start": cursor, "duration": metadata["duration"],
                           "audio": (folder / (scene["id"] + ".wav")).relative_to(ROOT).as_posix()})
            captions.extend([{**cue, "start": cue["start"] + cursor, "end": cue["end"] + cursor} for cue in metadata["cues"]])
            cursor += metadata["duration"]
            atomic_json(ROOT / "audio/progress.json", {"episode": episode["id"], "scene": scene["id"],
                        "seconds_completed": cursor, "engine": ENGINE, "updated": time.strftime("%Y-%m-%d %H:%M:%S")})
        temporary = folder / "narration.wav.part"
        with sf.SoundFile(temporary, mode="w", samplerate=RATE, channels=1, format="WAV", subtype="PCM_16") as combined:
            for scene in scenes:
                audio, sample_rate = sf.read(ROOT / scene["audio"], dtype="float32")
                combined.write(audio)
        temporary.replace(folder / "narration.wav")
        timeline = {**episode, "duration": cursor, "scenes": scenes, "captions": captions,
                    "voice": args.voice, "rate": args.rate, "engine": ENGINE,
                    "subtitle_timing": "Actual provider word boundaries; original acronyms restored when alignment is exact.",
                    "within_requested_range": 360 <= cursor <= 480,
                    "generation_seconds": time.monotonic() - started}
        atomic_json(folder / "timeline.json", timeline)
        (folder / "subtitles.srt").write_text("\n\n".join(f"{index + 1}\n{timestamp(cue['start'])} --> {timestamp(cue['end'])}\n{cue['text']}" for index, cue in enumerate(captions)) + "\n", encoding="utf-8")
        print(json.dumps({"episode": episode["id"], "duration": round(cursor, 2), "scene_count": len(scenes),
                          "status": "audio_complete", "within_requested_range": timeline["within_requested_range"],
                          "generation_seconds": round(timeline["generation_seconds"], 2)}), flush=True)
        if not timeline["within_requested_range"]:
            raise RuntimeError("Episode duration outside 360-480 seconds. Regenerate with another --rate; cached variants are retained.")


if __name__ == "__main__":
    asyncio.run(main())

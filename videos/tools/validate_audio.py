"""Validate finished narration, caption bounds, and correspondence to current scripts."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--episode")
args = parser.parse_args()
episodes = json.loads((ROOT / "scripts/episodes.json").read_text(encoding="utf-8"))
if isinstance(episodes, dict):
    episodes = episodes["episodes"]
if args.episode:
    episodes = [episode for episode in episodes if episode["id"] == args.episode]
results, errors = [], []
for episode in episodes:
    eid, folder = episode["id"], ROOT / "audio" / episode["id"]
    try:
        timeline = json.loads((folder / "timeline.json").read_text(encoding="utf-8"))
        info = sf.info(folder / "narration.wav")
        assert info.channels == 1 and info.samplerate == 24000, "Unexpected audio format"
        assert abs(info.duration - timeline["duration"]) < 1 / info.samplerate, "WAV and timeline differ"
        assert 360 <= info.duration <= 480, "Duration outside requested range"
        assert len(timeline["scenes"]) == len(episode["scenes"]), "Scene count differs"
        assert len(timeline["captions"]) >= len(episode["scenes"]), "Missing captions"
        cursor, alignment = 0.0, Counter()
        for scene, recorded in zip(episode["scenes"], timeline["scenes"]):
            assert all(recorded.get(key) == value for key, value in scene.items()), "Current script differs: " + scene["id"]
            assert abs(recorded["start"] - cursor) < 1 / info.samplerate, "Scene continuity error"
            meta = json.loads((folder / (scene["id"] + ".json")).read_text(encoding="utf-8"))
            digest = hashlib.sha256(json.dumps({"narration": scene["narration"], "voice": timeline["voice"],
                "rate": timeline["rate"], "engine": timeline["engine"], "captionVersion": 1}, sort_keys=True).encode()).hexdigest()
            assert meta["hash"] == digest, "Narration cache does not match current script"
            scene_info = sf.info(ROOT / recorded["audio"])
            assert abs(scene_info.duration - recorded["duration"]) < 1 / info.samplerate, "Scene WAV differs"
            cursor += recorded["duration"]
            alignment[meta["caption_alignment"]] += 1
        assert abs(cursor - info.duration) < 1 / info.samplerate, "Scene total differs"
        previous = -1.0
        for cue in timeline["captions"]:
            assert 0 <= cue["start"] < cue["end"] <= timeline["duration"], "Caption outside audio"
            assert cue["start"] >= previous - 0.001, "Overlapping or unordered captions"
            assert cue["text"].strip(), "Empty caption"
            previous = cue["end"]
        peak, energy, samples = 0.0, 0.0, 0
        for block in sf.blocks(folder / "narration.wav", blocksize=65536, dtype="float32"):
            assert np.isfinite(block).all(), "Invalid audio sample"
            peak = max(peak, float(np.max(np.abs(block))))
            energy += float(np.sum(block.astype(np.float64) ** 2))
            samples += len(block)
        rms = (energy / samples) ** .5
        assert peak > .01 and rms > .001, "Audio is silent or unexpectedly quiet"
        assert peak < 1, "Audio clipping detected"
        results.append({"episode": eid, "seconds": info.duration, "scenes": len(timeline["scenes"]),
                        "captions": len(timeline["captions"]), "alignment": dict(alignment), "peak": peak,
                        "rms": rms, "rate": timeline["rate"], "voice": timeline["voice"], "valid": True})
    except (AssertionError, OSError, ValueError, KeyError) as error:
        errors.append({"episode": eid, "error": str(error)})
report = {"requestedEpisodes": len(episodes), "validatedEpisodes": len(results), "episodes": results, "errors": errors,
          "totalSeconds": sum(result["seconds"] for result in results),
          "scope": "Technical validation; no automatic speech-recognition or human listening claim"}
target = ROOT / "qa" / ("audio-validation.json" if not args.episode else f"audio-validation-{args.episode}.json")
target.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report))
sys.exit(0 if not errors and results else 1)

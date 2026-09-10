# English AI narration engine

The production narrator is Microsoft Edge's **en-US-JennyNeural**, accessed through the open-source `edge-tts` Python package. This uses an online service. Only the course's synthetic teaching scripts are sent for synthesis. No personal voice is cloned.

From the `videos` directory, install the pinned dependencies before generating narration:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r tools\requirements-voice.txt
.\.venv\Scripts\python.exe tools\synthesize_edge.py --episode 01 --rate=+0%

# Continue from episode 02, keeping episode 01 untouched.
.\.venv\Scripts\python.exe tools\synthesize_edge.py --from-episode 02 --rate=+0%

# Restore readable source wording using the saved provider timestamps.
# This never synthesizes or modifies audio.
.\.venv\Scripts\python.exe tools\repair_captions.py --all

# Validate finished audio, actual script versions and subtitles.
.\.venv\Scripts\python.exe tools\validate_audio.py
```

`--rate` changes the neural voice's natural speaking rate. Audio is never stretched. Each finished episode must measure 360–480 seconds; otherwise the command exits with an explicit duration error. Regenerate only that episode at an adjusted rate, aiming near 420 seconds. For example, increase the rate if an episode exceeds 480 seconds. Resume the following episode after the correction.

Every scene has a hash of its original narration, voice, rate, package version and caption mapping version. Its WAV, original MP3 and metadata are retained under `audio/<episode>/.cache`. Identical settings reuse the cache. Changing the rate keeps the earlier variant. The script retries transient requests three times and checkpoints after each completed scene in `audio/progress.json`.

The output contract matches the video producer:

- `audio/<episode>/<scene>.wav` and `.json`: scene audio and metadata.
- `audio/<episode>/narration.wav`: continuous 24 kHz mono PCM audio.
- `audio/<episode>/timeline.json`: scene starts/durations/audio paths plus caption starts/ends/text.
- `audio/<episode>/subtitles.srt`: reusable English subtitles.

Subtitles use the provider's actual WordBoundary timestamps. Acronym expansions such as “T N Z” map back to the original readable “TNZ” when the character alignment is exact. If the provider's tokenization cannot be mapped exactly, captions retain its actual words and timestamps. The script does not invent or distribute word timings proportionally. Short 0.6-second lead and 0.65-second tail pauses separate teaching scenes; these are not used to force an episode into the requested duration range.

Verified benchmark: a 47-word JennyNeural sample at -10% generated a 23.136-second MP3 in 4.109 seconds. Episode 01 at +0% generated 423 seconds of narration in 43.985 seconds, with 12 scenes and 84 valid caption cues. Every episode-01 caption mapped to its original script wording; WAV and timeline duration matched. See `qa/edge-episode-01-validation.json` and `qa/edge-voice-sample.json`.

Production completed on 2026-09-09: **12 episodes, 144 scenes, 1,020 caption cues, 87 minutes 19.464 seconds**. All episodes use JennyNeural at +0%, and all measured between 423.000 and 451.992 seconds. `qa/audio-validation.json` records 12 valid episodes and zero errors, including current source hashes, scene continuity, actual WAV duration, subtitle boundaries, finite audio and nonzero signal. This is technical validation; it does not claim human listening or speech recognition.

Caption mapping revision 2 handles provider boundaries containing multiple original words. The repair command preserves exact source punctuation and acronyms while retaining the saved provider timestamps. It changed no audio: before/after SHA-256 verification covered 444 media files across the 12 episodes. Episode IDs come from `scripts/episodes.json`; render prototypes 00 and 98 are excluded from this production count.

The locally downloaded Kokoro assets are also present and verified against official release hashes, but the CPU pilot on this workstation was substantially slower. Existing ONNX Runtime exposed CPU and Azure providers, with no CUDA or DirectML provider enabled. The production engine therefore uses the measured online neural voice path. Provider availability is separate from the locally cached completed narration.

Primary sources: [edge-tts project and supported usage](https://github.com/rany2/edge-tts), [Kokoro ONNX official project](https://github.com/thewh1teagle/kokoro-onnx).

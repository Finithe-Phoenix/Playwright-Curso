# Playwright in Motion

The motion edition adds progressive code reveals, animated request paths, large kinetic titles, prompt walkthroughs and recorded browser interactions to the twelve English lessons. The original baseline remains under `videos/renders`.

## Cinematic focus edition

The library now opens the cinematic version. Use **Compare: original** to switch to the previous edit at the same timestamp. **Watch: cinematic** switches back. Both exports retain the same chapter timing and English narration.

This pass adds editorial close-ups, animated panel entrances, stronger typography and quiet transition cues. It reuses the verified Hyperframes exports and original captured interactions; it does not claim a new test run or a live assistant session. The full caption band stays fixed. The `cinema` folder contains the new MP4 files, shot decisions and review evidence. Regenerate with `python videos/tools/direct_cinema.py --episode all`; run it from the repository root with FFmpeg, NumPy and SoundFile installed. The supplied static font was instantiated from the bundled Source Sans variable font at weight 750 using FontTools.

## Watch

From the repository root:

```powershell
node videos/tools/serve-course.mjs --port 8767
```

Open http://127.0.0.1:8767/videos/motion/index.html. Start with the 2:36 bonus walkthrough, then choose a lesson and use the chapter buttons or the native video controls. Use Focus mode to hide the chapter sidebar. A link ending in `#02@85` opens lesson 02 at 85 seconds. Full screen gives code and terminal text the most room.

The `transcripts` folder contains the English narration for all twelve lessons.

## What the footage shows

- Browser segments are real Playwright recordings against the local synthetic application. The capture suite checks the response, balance, canonical transfer count and cleanup.
- The unavailable-service recording intercepts the browser request with a 503 response. It demonstrates UI recovery, not a real server outage.
- The successful browser recording and terminal result share the exact same transaction reference. TNZ communicates with the local simulator over a real TN3270 socket. This does not establish behavior on a production mainframe.
- Code is displayed as a teaching walkthrough. Python and Java examples demonstrate the equivalent browser contract; a shared browser recording is not presented as a separate recording of each language runtime.
- Prompt scenes are animated, reusable teaching inputs. They are not a recording of a live assistant generating or executing a response.
- Reading pauses and final-frame holds are editorial. They are not recommended synchronization techniques for regression tests. The captured application's interactions retain their recorded speed; code emphasis is aligned to recorded action timestamps where available.

## Source and verification

`compositions` contains editable Hyperframes HTML and timed audio. `captures` contains the original browser recordings, screenshots, action timestamps and terminal screen. `renders` contains final MP4 files and media metadata. `progress.json` records export state; an export is separate from visual review.

The English application contract was verified with 22 tests: ten distributed TypeScript cases, eight Python cases, three Java cases and one TypeScript hybrid case. The separate three-case recording suite also passed. Episode 08 includes a separate, intentionally failing replay test against the seeded duplicate-transfer defect: the observed balance is 80000 minor units and the canonical transfer count is two. This failure is kept distinct from the healthy run. Python reports a TNZ event-loop deprecation warning; the Java runner reports a native-stream warning with successful JUnit results.

The English narration is retained from the baseline except episode 07's changed message-language reference. That scene was updated with matching word-timed captions. New media uses blue, gray and white without green or teal accents.

## Teach and review

Use [the two-hour workshop guide](../../docs/TEACH-WITH-MOTION.md) to alternate short clips with hands-on exercises. The twelve full lessons remain 6â€“8 minutes each. `qa/summary.json` records media checks and sampled visual review; it does not claim uninterrupted human playback of every lesson. Full-resolution extracted frames and raw runner artifacts stay in ignored `local-results` folders; the published contact sheets and captured observations provide reviewable evidence.

## Reproduce the edition

Use the pinned Hyperframes version in `videos/package.json` and the existing voice/render Python requirements. Start the local application on port 3600 and the simulator on 2423. Set the matching `BASE_URL`, `TEST_HOOK_KEY`, `TNZ_PYTHON` and `TNZ_PORT` values before running the recording suite.

```powershell
cd videos/lab/distributed
npm ci
npx playwright test --config recording/record.config.ts
```

From the repository root, using a Python environment with the documented voice dependencies:

```powershell
python videos/tools/prepare_motion_media.py
python videos/tools/render_motion.py --cli videos/node_modules/hyperframes/dist/cli.js
```

The capture configuration uses installed Microsoft Edge. The render script currently uses the standard Windows Chrome installation path. Adjust these explicit local prerequisites for another workstation; no system-wide browser settings are changed. Final rendering is sequential and resumes by content fingerprint. Keep baseline evidence intact and store new run artifacts under `local-results`.

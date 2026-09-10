# Playwright Course

An advanced two-hour workshop with twelve companion video lessons, local distributed services, TypeScript, Python and Java test projects, and a local TN3270 training simulator.

## Published baseline

`v1.0.0-baseline` preserves the existing course before the English-language and laboratory improvements. Some original pages, application labels and documents are still Spanish. The recordings are in English. This release records the starting point; it does not claim that the language migration has already happened.

- Twelve final 1080p MP4 lessons, approximately 87 minutes in total: [`videos/renders`](videos/renders).
- Narration WAV files, timed subtitles and timelines: [`videos/audio`](videos/audio).
- Editable HTML compositions and their media: [`videos/compositions`](videos/compositions).
- Distributed application and test suite: [`videos/lab/distributed`](videos/lab/distributed).
- Python TN3270 simulator, TNZ adapter, and Java/Python/TypeScript examples: [`videos/lab/mainframe`](videos/lab/mainframe).
- Course documents, copyable prompts and visual review evidence are included.

The blue, gray and white design is the course standard. Do not introduce green or teal accents.

## Open the course

After cloning, use Node.js 22 or later:

```powershell
node videos/tools/serve-course.mjs
```

Open [the video library](http://127.0.0.1:8766/videos/index.html) or [the course guide](http://127.0.0.1:8766/CURSO-PLAYWRIGHT-IA.html). The server supports video seeking. Stop it with Ctrl+C in its terminal.

## Run the application

From the repository root, in PowerShell:

```powershell
node scripts/start-demo.mjs
```

Open [TransferLab](http://127.0.0.1:3300/transfers). The launcher starts three services and prints a fresh synthetic login. No Docker or dependency installation is required for the application. See the [quick-start guide](docs/QUICKSTART.md) for test runners, alternate ports and verification.

All services bind to localhost. Training data is synthetic and lives in memory. The TN3270 endpoint is a local simulator, not z/OS or CICS.

## Versioned media and download

The final MP4 files and WAV narration are ordinary Git files, included in a normal clone. No Git LFS installation is required for this baseline. Dependencies, browser installations, model caches, temporary renders and personal environment files are excluded.

The complete viewing ZIP is attached to the [baseline release](https://github.com/Finithe-Phoenix/Playwright-Curso/releases/tag/v1.0.0-baseline). `COURSE-MANIFEST.json` describes that original ZIP; Git is authoritative for additional repository files and subsequent changes.

## Verification scope

The new launcher passed a three-service API smoke check covering transfer, sequential replay, ledger identity and cleanup. This does not replace browser regression or the preserved baseline evidence.

The preserved evidence records 22 passing local tests and visual review of 144 sampled frames from the twelve final videos. These are recorded production-workstation results, not a claim that tests have already run on your computer. Full playback and listening are distinct from the recorded sampled visual review. See [`videos/qa/VIDEO-REVIEW.md`](videos/qa/VIDEO-REVIEW.md).

## Improvement and regression kit

- [English improvement plan and acceptance gates](docs/IMPROVEMENT-PLAN.md).
- [One-command local application and testing quick start](docs/QUICKSTART.md).
- [Twelve copy-and-paste prompts](docs/PROMPTS.md): discovery, critical paths, coverage, generation, reports, Excel intake and review.
- [Excel test-case template](templates/test-cases-template.xlsx): three synthetic examples and nine steps, all requiring review.

The new plan, launcher, prompt pack and template are in English. Full course/UI language migration and related video updates are planned work; the baseline remains preserved.

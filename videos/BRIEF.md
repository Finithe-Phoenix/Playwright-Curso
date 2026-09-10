---
workflow: general-video
flow: automation
storyboard: no
message: Build and verify a local regression across a browser, distributed services, and a TN3270 training terminal using the same business evidence.
destination: Local course and reusable training videos
aspect: 16:9
language: en
audience: Advanced QA automation engineers and developers using Java, TypeScript, or Python
length: 12 episodes, 6–8 minutes each
---

# Playwright across distributed systems and a training mainframe

## Confirmed requirements

The user requested at least ten actual videos made with Hyperframes, AI narration in clear English, and step-by-step Playwright implementation for distributed applications and mainframe applications using TNZ. They selected 6–8 minutes per episode and confirmed that every participant must run the demonstration locally because no mainframe test environment is available.

The latest visual request calls for improved teaching slides in blue, gray and white. Apply the nine palette values and their roles in [DESIGN.md](DESIGN.md) consistently, including code, terminal results, captions and active animation states. This is a visual revision: preserve the existing scripts, English voice, scene timing and subtitle timing. Previous exports must not be presented as the revised design before they are rebuilt and reviewed.

## Production decisions

Produce twelve episodes. Use the existing Spanish course as the curriculum, with English narration and English subtitles. Frame code, diagrams, local application evidence, and a TN3270 terminal simulation as a tutorial. Render with Hyperframes locally. Generate a generic English neural voice with Microsoft Jenny through the open-source edge-tts client. The completed narration files play locally. A verified Kokoro model is retained as an optional local alternative. The narration is synthetic and is not a clone of an individual.

Use a 1920×1080 canvas and 24 frames per second, subject to a measured local render benchmark. Prioritize legible code and synchronized explanation. Use one render worker initially because the host has limited free RAM. Save progress after each scene and episode; preserve completed audio and video on resume.

## Accuracy

Playwright automates the browser and HTTP APIs. IBM TNZ communicates with the TN3270 terminal. The local terminal is a protocol simulator, not z/OS, CICS, or DB2. Its display obtains data from the same authoritative Accounts records; it demonstrates orchestration and protocol integration, not independent reconciliation against a real mainframe.

Distinguish measured execution from expected output and illustrative fragments in captions, scripts, and companion code. Never fabricate a passed test result. Keep every example on synthetic local data.

## Authorization and review

The user explicitly requested generated narrated videos. Proceed through local creation, review, and rendering under that authorization. Review composition checks, representative frames, audio integrity, duration, and subtitle boundaries before delivery. No publication or external account creation is requested.

## Relationship to the two-hour workshop

The series supplies 72–96 minutes of preparation and review material. Use selected excerpts during the existing two-hour live workshop; do not add the entire series to the live agenda.

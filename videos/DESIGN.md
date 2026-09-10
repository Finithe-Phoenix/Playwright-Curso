# Visual direction — blue, gray and white

The user's latest direction replaces the previous palette with blue, cool gray and white and calls for clearer teaching slides. This document describes the revised design target. Existing MP4s and screenshots only demonstrate this revision after they have been rebuilt and reviewed against their current source hashes.

The course remains an engineering field guide that follows one transfer from browser action to authoritative application evidence, then to the training terminal. Preserve every script, scene duration, narration file, subtitle cue and business assertion during the visual revision.

## Palette and roles

| Color | Role |
|---|---|
| `#FFFFFF` | Main canvas, cards and neutral surfaces |
| `#F4F7FC` | Secondary canvas and quiet section backgrounds |
| `#14213D` | Main headings and body text |
| `#2457E6` | Blue accent, active step, selected line marker and progress |
| `#EAF0FF` | Light blue selected-card and emphasis background |
| `#56647A` | Secondary text on light surfaces |
| `#D7DFED` | Borders, dividers, and secondary text on dark code surfaces |
| `#111C34` | Code, terminal and subtitle surfaces |
| `#EEF3FF` | Code, terminal and subtitle text on dark surfaces |

Use these roles consistently across title cards, body slides, architecture nodes, active animation states, code comments, terminal transcripts, captions, progress indicators and evidence labels. Animated colors need the same palette as the initial frame. The training terminal uses navy and light text; its protocol does not require a particular display color. Keep its TRAINING SIMULATOR label visible.

Calculated foreground/background contrast ratios are 15.97:1 for main navy on white, 5.86:1 for blue on white, 6.00:1 for secondary gray on white, and 15.25:1 for light code text on its navy surface. These are calculations for solid color pairs, not a certification of rendered frames. Use the lighter `#D7DFED` for code comments and line numbers on navy; reserve `#56647A` for light backgrounds.

## Layout and typography

Canvas: 1920×1080, 16:9. Keep at least 90 px of horizontal safe space. Main teaching content should finish above y=880, followed by its evidence/source label. Reserve a separate subtitle band around y=930–1080, with generous horizontal padding. A caption must never cover code, evidence or the footer.

Keep a compact episode/step header, then one dominant title and one main teaching surface. Reduce the empty gap between heading and content instead of reducing the code font to fit. Opener numbers identify the chapter; they should not outweigh the lesson outcome. Avoid repeated large branding or decorative panels that compete with the teaching material.

Use the bundled Source Sans 3 and JetBrains Mono fonts. Target titles at 60–72 px, teaching text at 33–38 px, code at 25–31 px and captions at 31–34 px. Review the longest title and longest code panel at actual export resolution. Preserve indentation and literal operator characters; disable code-font ligatures so `===`, `!==`, `<=` and `=>` retain their source spelling. Full files remain available in the companion lab.

## Scene families

- **Chapter opener:** short outcome statements on clear cards, one compact episode marker, and visible reading order.
- **Steps and recap:** white cards against a light gray field, blue number markers, restrained borders, and an active blue edge or pale blue background. Do not rely on text color alone to indicate focus.
- **Source code:** navy code panel, high-contrast text, readable line-number column, and blue emphasis on the active line. Keep supporting instructions separate from the code and preserve the source/illustration label.
- **Architecture:** factual paths with consistent node sizes and spacing. Use arrows only for a real dependency or an explicitly described workflow. Independent observations belong in separate rows; terminal lookup reads Accounts, while Ledger is a separate delayed projection.
- **Application and terminal evidence:** allocate enough space to read the transaction amount, status and reference. Align the browser evidence and terminal result for comparison. Keep captures proportionate and their data intact; use freshly captured local evidence when the application's appearance changes.

Every instructional scene should retain its concrete action, observation and reason. The redesign changes their visual hierarchy rather than adding narration or altering the underlying examples.

## Motion and review

Preserve scene boundaries and the existing short entrances and emphasis intervals. Use restrained, seek-safe animation. A blue border, background or line marker can move attention without shifting the text during reading. Stable reading periods are intentional. No music bed is needed.

Rebuild the compositions and any embedded screenshots affected by the new application theme. Before reviewing a final MP4, confirm that production records match the current builder, timeline, evidence assets and artifact SHA-256. Review the twelve actual midpoint frames per episode and expand dense code or evidence frames when needed. Inspect caption contrast, active-state colors, clipping and corrected architecture paths. Keep the scope explicit: sampled-frame review does not establish complete playback or audio listening.

Historical pilot images, calibration videos and previous contact sheets are diagnostic evidence of their own revision. They should not serve as current course previews or be mistaken for approval of the revised appearance.

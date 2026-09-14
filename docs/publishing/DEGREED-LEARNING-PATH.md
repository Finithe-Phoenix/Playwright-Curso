# Advanced Playwright: From Prompt to Proof

## Short course description

Build reliable regression tests with Playwright in TypeScript, Python and Java. Follow browser actions across distributed services, connect a local 3270 simulator through TNZ, and use AI-assisted prompts to design tests, investigate failures and report evidence clearly.

## About this learning path

This advanced learning path connects test design with observable business outcomes. Explore isolated test data, authentication, API assertions, eventual consistency, network mocks and trace-based debugging. Extend the workflow across browser and terminal interfaces using a local TN3270 simulator and a Python TNZ adapter. Finish with a capstone that turns application evidence into focused regression cases and a clear execution report.

**Audience:** QA automation engineers, SDETs and developers with browser automation experience.

**Prerequisites:** Familiarity with Playwright, API testing and at least one of TypeScript, Python or Java. Consult the repository quickstart for local dependencies.

**Language:** English narration and on-screen material.

**Format:** Twelve lessons of approximately 7â€“8 minutes and an optional introductory showcase. The two-hour facilitated workshop uses selected clips and exercises; completing all videos and exercises independently may take longer.

**Learning outcomes:** Design business-focused regression assertions; manage isolated test lifecycles; verify distributed state with correlation and bounded polling; distinguish mocked and real execution evidence; connect browser tests to a local terminal adapter; review AI-assisted test proposals and report results accurately.

**Suggested skills:** Playwright, Regression Testing, TypeScript, Python, Java, API Testing, Distributed Systems, Test Isolation, Trace Analysis, TNZ, TN3270, AI-Assisted Testing.

## Cover image

Use the [series preview cover](thumbnails-v2/showcase.png) for the learning path. Each video now has its own thumbnail, linked below. Browse the [thumbnail gallery](thumbnails-v2/index.html).

**Alternative text:** Playwright series preview with a navy title panel beside a laptop and test checklist.

## Publishing notes

Start with the optional introduction, then publish lessons 01â€“12 in order. Copy each title and description into its learning item. The MP4 paths below are relative to the repository root. Upload the files through your organization's approved media workflow and use learner-accessible links. Do not publish localhost URLs as learner links.

Browser segments show recorded local demonstrations. Terminal exercises use a local training simulator rather than a corporate mainframe. Playwright handles browser automation; TNZ handles the terminal protocol.

## Optional introduction

### Title

From Prompt to Proof: A Live Lab Walkthrough

### Description

Preview the regression workflow from a precise prompt to observable evidence. Follow a recorded browser transfer across local services and reconcile the same transaction through a TNZ terminal adapter. See how TypeScript, Python and Java express the same business checks and why a passing status alone is not enough.

**Video:** `videos/motion/cinema/showcase-cinema.mp4`

**Thumbnail:** [Download PNG](thumbnails-v2/showcase.png)

**Duration:** 2:36

## Lesson 01

### Title

Build the Local Test Architecture

### Description

Prepare the local training architecture and identify what each component can prove. Explore browser, API and service boundaries; review the TypeScript, Python and Java setup; and define successful transfers, insufficient funds and sequential replay as separate regression cases. Learn to express money precisely and confirm readiness before testing.

**Video:** `videos/motion/cinema/01-cinema.mp4`

**Thumbnail:** [Download PNG](thumbnails-v2/01.png)

**Duration:** 7:03

## Lesson 02

### Title

TypeScript: Reliable UI and API Regression

### Description

Build a TypeScript regression test around observable business behavior. Use accessible locators, capture the relevant response and verify both the account balance and transfer record. Extend the workflow to insufficient funds and sequential idempotency checks, then review suggested changes without weakening the assertions.

**Video:** `videos/motion/cinema/02-cinema.mp4`

**Thumbnail:** [Download PNG](thumbnails-v2/02.png)

**Duration:** 7:10

## Lesson 03

### Title

Python: Fixtures That Own Their Data

### Description

Create Python fixtures that own their test data and release resources reliably. Separate setup requests from the authenticated browser context, verify visible behavior and response semantics, and retain traces before cleanup. Explore rejected transfers and sequential replay while preserving the original failure.

**Video:** `videos/motion/cinema/03-cinema.mp4`

**Thumbnail:** [Download PNG](thumbnails-v2/03.png)

**Duration:** 7:23

## Lesson 04

### Title

Java: JUnit Lifecycle and Evidence

### Description

Implement the regression workflow with Playwright for Java and JUnit. Define ownership of browser contexts and data, use locator assertions and inspect integer monetary values. Add rejection and replay cases, preserve trace evidence and recognize why shared mutable resources can make parallel tests unreliable.

**Video:** `videos/motion/cinema/04-cinema.mp4`

**Thumbnail:** [Download PNG](thumbnails-v2/04.png)

**Duration:** 7:19

## Lesson 05

### Title

Isolation, Authentication and Test Data

### Description

Make regression tests independent through deliberate data ownership and authentication boundaries. Explore storage-state reuse, retry isolation, partial setup failures and cleanup after evidence capture. Use a lifecycle audit to identify hidden coupling before increasing concurrency.

**Video:** `videos/motion/cinema/05-cinema.mp4`

**Thumbnail:** [Download PNG](thumbnails-v2/05.png)

**Duration:** 7:20

## Lesson 06

### Title

Distributed Workflows: Correlation and Polling

### Description

Follow one business transaction across three local services. Capture its correlation identifier, verify authoritative account state and poll the delayed ledger projection with a bounded wait. Learn why polling must observe state rather than repeat the transfer, and build a useful timeline when consistency checks fail.

**Video:** `videos/motion/cinema/06-cinema.mp4`

**Thumbnail:** [Download PNG](thumbnails-v2/06.png)

**Duration:** 7:14

## Lesson 07

### Title

Mocks and Real End-to-End Evidence

### Description

Use a narrowly scoped network mock to test a controlled UI error path, then inspect the real state left behind. Compare evidence from a mocked boundary with a real end-to-end run. Learn to remove route handlers, label results accurately and distinguish browser behavior from backend resilience.

**Video:** `videos/motion/cinema/07-cinema.mp4`

**Thumbnail:** [Download PNG](thumbnails-v2/07.png)

**Duration:** 7:04

## Lesson 08

### Title

Traces, CI and Evidence-Based Debugging

### Description

Investigate an intentionally failing replay case using the request, trace and monetary assertions. Build a bounded diagnostic prompt, validate the corrected path and plan CI readiness and evidence retention. Distinguish observed local results from CI execution that has not occurred.

**Video:** `videos/motion/cinema/08-cinema.mp4`

**Thumbnail:** [Download PNG](thumbnails-v2/08.png)

**Duration:** 7:15

## Lesson 09

### Title

Local 3270 Architecture and TNZ Setup

### Description

Extend the local lab with a TN3270 training simulator and the Python TNZ library. Separate browser control from terminal protocol automation, inspect input and result fields, and try an unknown transfer reference. Understand the simulator boundary before applying the pattern to a real mainframe environment.

**Video:** `videos/motion/cinema/09-cinema.mp4`

**Thumbnail:** [Download PNG](thumbnails-v2/09.png)

**Duration:** 7:20

## Lesson 10

### Title

TNZ Sessions: Fields, Waits and Cleanup

### Description

Build a predictable TNZ adapter with bounded connection and screen waits. Check keyboard readiness, enter a validated reference, wait for the matching result and parse labeled business values. Preserve screen evidence and release the session reliably, including negative outcomes.

**Video:** `videos/motion/cinema/10-cinema.mp4`

**Thumbnail:** [Download PNG](thumbnails-v2/10.png)

**Duration:** 7:14

## Lesson 11

### Title

Hybrid Regression: One Correlation Across Interfaces

### Description

Connect browser and terminal evidence around one transfer. Extract the canonical correlation identifier, call the Python TNZ adapter from language-specific workflows and reconcile the reference, amount, currency and balance. Keep the delayed ledger check distinct and collect evidence before cleanup. This demonstration uses a local training simulator.

**Video:** `videos/motion/cinema/11-cinema.mp4`

**Thumbnail:** [Download PNG](thumbnails-v2/11.png)

**Duration:** 7:25

## Lesson 12

### Title

AI-Assisted Regression Capstone

### Description

Bring the workflow together in an evidence-driven regression capstone. Give an assistant the actual application contract, request a risk and evidence matrix, and generate one complete case before expanding the suite. Audit assertions, investigate failures with focused prompts and write a report that distinguishes passed, failed, blocked and unexecuted work.

**Video:** `videos/motion/cinema/12-cinema.mp4`

**Thumbnail:** [Download PNG](thumbnails-v2/12.png)

**Duration:** 7:32

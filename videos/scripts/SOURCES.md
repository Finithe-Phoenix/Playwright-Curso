# Script sources and production notes

These sources support the English narration and visual scripts in `episodes.json`. Primary documentation and the actual local laboratory source were checked while authoring on 2026-09-09. API names, runner differences, terminal calls and local endpoint behavior were cross-checked; the scripts are original instructional explanations, not excerpts copied from documentation.

## Script audit

- Exactly **12 episodes**, each containing **12 scenes**: 144 scenes total.
- **11,866 spoken words** across the narration fields.
- Each episode contains **969–999 spoken words**; individual scenes contain **71–85 words**.
- At an assumed 145 spoken words per minute, the narration is approximately **6 minutes 41 seconds to 6 minutes 53 seconds per episode**. This is an estimate, not a measured media duration. Inspect the final encoded audio/video durations before declaring the 6–8 minute requirement satisfied.
- On-screen code stays within **12 lines and 72 characters per line**. One route-handler excerpt uses 10 lines; all others use at most 9.
- Narration is English. Spanish UI labels intentionally match the local application's accessible-name contract and must not be translated inside executable locators.
- Code panels are excerpts or explicitly labeled prompt/report templates. Fixtures, imports and surrounding lifecycle code belong to the referenced project files. A displayed excerpt is not a standalone program or evidence of successful execution.

| Episode | Words | Main topic |
|---|---:|---|
| 01 | 969 | Architecture and language setup |
| 02 | 997 | TypeScript UI and API business regression |
| 03 | 978 | Python pytest fixtures and lifecycle |
| 04 | 997 | Java JUnit ownership and reporting |
| 05 | 999 | Isolation, authentication and test data |
| 06 | 981 | Distributed correlation and bounded polling |
| 07 | 990 | Mocked UI behavior and integrated evidence |
| 08 | 996 | Controlled defect, tracing and CI |
| 09 | 997 | Local TN3270 architecture and TNZ setup |
| 10 | 991 | TNZ fields, waits, parsing and cleanup |
| 11 | 996 | Hybrid browser, services and terminal |
| 12 | 975 | Copyable AI prompts and regression capstone |

The scripts instruct learners to inspect and record actual outcomes. They do not fabricate passing output. Current measured results belong to the laboratory verification files, and video production should use those artifacts for any result panels.

## Actual local implementation references

- [Original business contract and language mappings](../../03-LABORATORIO-Y-LENGUAJES.md): TR-01, TR-02 and TR-03 amounts, UI labels and core API behavior. This earlier planning document must be read alongside the implemented extension below.
- [Distributed laboratory README](../lab/distributed/README.md): real local startup, ports, browser selection, canonical versus projected state and controlled defect commands.
- [TypeScript fixtures](../lab/distributed/tests/fixtures.ts) and [regression cases](../lab/distributed/tests/regression.spec.ts): actual browser/API suite and lifecycle.
- [Distributed verification](../lab/distributed/evidence/VERIFICATION.md): measured healthy and controlled-defect runs; consult this rather than inferring results from source.
- [Terminal laboratory README](../lab/mainframe/README.md): actual setup scripts, runner commands, adapter contract and local simulation limits.
- [TNZ adapter](../lab/mainframe/adapter.py) and [simulator](../lab/mainframe/simulator.py): implemented field sequence, screen predicates, input validation, deadlines and shutdown.
- [Python hybrid test](../lab/mainframe/test_hybrid_browser.py), [TypeScript hybrid test](../lab/mainframe/typescript/hybrid.spec.ts), and [Java hybrid test](../lab/mainframe/java/src/test/java/training/HybridTransferTest.java): source-backed subprocess and business-value comparisons.
- [Python core regression](../lab/mainframe/test_core_regression.py) and [Java core regression](../lab/mainframe/java/src/test/java/training/CoreRegressionTest.java): additional core cases added to the language projects; inspect their current verification evidence for actual execution status.
- [Terminal and hybrid verification](../lab/mainframe/evidence/VERIFICATION.md): measured protocol and language-specific hybrid outcomes.

Paths above are relative to this file. Core regression generation and language-adaptation exercises must not be confused with the exact set of tests already implemented and measured in each project. In particular, language equivalence in an example is not evidence of executing that language's suite.

## Primary documentation

### Playwright foundations and TypeScript

- [Installation](https://playwright.dev/docs/intro): package/browser installation and test execution.
- [Locators](https://playwright.dev/docs/locators): accessible labels, roles and explicit test identifiers.
- [Assertions](https://playwright.dev/docs/test-assertions): locator assertions and `expect.poll` for bounded observations.
- [API testing](https://playwright.dev/docs/api-testing): authenticated API observations and browser-context cookie sharing.
- [Fixtures](https://playwright.dev/docs/test-fixtures): resource setup and teardown around tests.
- [Authentication](https://playwright.dev/docs/auth): storage-state reuse and account ownership considerations.
- [Isolation](https://playwright.dev/docs/browser-contexts): separate browser contexts; server-side fixture ownership remains a laboratory design concern.
- [Retries](https://playwright.dev/docs/test-retries): runner attempts and worker lifecycle.
- [Timeouts](https://playwright.dev/docs/test-timeouts): bounded execution and assertion timing.
- [Mock APIs](https://playwright.dev/docs/mock), [network](https://playwright.dev/docs/network), and [Route API](https://playwright.dev/docs/api/class-route): interception, continuing requests and fulfilling controlled responses.
- [Trace viewer](https://playwright.dev/docs/trace-viewer): trace inspection and diagnostics.
- [CI setup](https://playwright.dev/docs/ci-intro) and [reporters](https://playwright.dev/docs/test-reporters): job preparation, runner output and artifacts.
- [Best practices](https://playwright.dev/docs/best-practices): test behavior, isolation and locator design.

### Python and Java

- [Playwright Python installation](https://playwright.dev/python/docs/intro), [pytest plugin reference](https://playwright.dev/python/docs/test-runners), and [Python API testing](https://playwright.dev/python/docs/api-testing): synchronous API, fixture scope and runner-specific options.
- [pytest fixture documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html): yielding fixtures and failure-aware teardown design.
- [Playwright Java test runners](https://playwright.dev/java/docs/test-runners), [multithreading](https://playwright.dev/java/docs/multithreading), and [tracing API](https://playwright.dev/java/docs/api/class-tracing): JUnit integration, object ownership and library trace limitations.
- [Maven Surefire](https://maven.apache.org/surefire/maven-surefire-plugin/): test execution and report locations.

### TNZ and process orchestration

- [IBM TNZ repository](https://github.com/IBM/tnz), [overview](https://ibm.github.io/tnz/), and [API reference](https://ibm.github.io/tnz/tnz/): actual `Tnz`, `connect`, `wait`, `scrstr`, field-input methods, `enter` and `shutdown`.
- [IBM TNZ security](https://ibm.github.io/tnz/security/): transport and verification settings. The classroom adapter deliberately uses plaintext only on loopback; no real-host connection is demonstrated.
- [Python monotonic clock](https://docs.python.org/3/library/time.html#time.monotonic): deadline measurement.
- [Python subprocess](https://docs.python.org/3/library/subprocess.html): argument lists, output capture and timeout behavior.
- [Node child processes](https://nodejs.org/api/child_process.html): executable-file invocation and millisecond timeouts.
- [Java ProcessBuilder](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ProcessBuilder.html): passing executable arguments and owning child processes.

## Claims and boundaries to preserve in production

1. `GET /api/transfers` reads immediate canonical Accounts state. `GET /api/ledger/transfers` reads a separate, eventually consistent projection. Poll only the latter observation where the local contract permits delay.
2. The account debit, canonical record and event update together in one local in-memory process. No durable database, broker, multi-node transaction or crash-recovery guarantee is established.
3. The terminal simulator queries `/__test/lookup`, which reads the same authoritative in-memory Accounts data. A terminal match is additional protocol/presentation evidence, not independent mainframe reconciliation or durable storage evidence.
4. TR-03 repeats a request sequentially. It does not establish concurrent idempotency.
5. TR-05 supplies a browser response. It checks UI error behavior; it does not establish genuine backend outage recovery.
6. Actual local runs, configured CI and executed hosted CI must remain separate report states.
7. Final video duration, English subtitle alignment, legibility and intelligible narration require inspection of the rendered media; word counts alone do not verify them.

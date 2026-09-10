# Course and laboratory improvement plan

## Starting point

The complete baseline was published first as `v1.0.0-baseline`, commit `de97c7ebc1d6dffca5347d52f4ce7661ea73e2ac`. It includes twelve videos, narration sources, editable compositions, the distributed application, the TN3270 simulator, three language routes and recorded verification evidence. The release ZIP is available on GitHub.

This document proposes the next course revision. The English-only migration and expanded application are **planned**, not already implemented. The new quick-start launcher, this plan, the prompt pack and Excel template are delivered now. Do not overwrite the preserved baseline or describe old screenshots and test results as evidence of a new application version.

## Editorial and design requirements

- Use English throughout the guide, navigation, application labels, messages, test descriptions, reports, prompts, subtitles and visible code comments. Translate prose around code; change selectors and assertions only alongside the actual application contract.
- Keep a concise course title and describe the videos as **English narration**. Remove production-origin badges and repetitive promotional footers from the learner interface. Keep dependency licenses and accurate technical verification records.
- Preserve blue, gray and white. No green or teal accents, including success states and course-owned reports. Standard third-party reports may need a separate neutral summary rather than unsafe changes to their dependencies.
- Use one term consistently for each concept: source account, beneficiary, transfer reference, available balance, canonical record and ledger projection.
- Distinguish a complete runnable example from a slide excerpt. Link every excerpt to its exact repository file and release.
- Keep mainframe terminology accurate: Playwright handles browser/API interactions; TNZ handles TN3270. The supplied terminal is a local simulator, not a real z/OS or CICS environment.

## Ordered implementation

| Priority | Work | Concrete completion evidence |
|---|---|---|
| P0 / 1 | English-only contract and content | An inventory of every learner-facing string; updated UI, API messages, selectors and assertions across all three languages; review finds no unintended Spanish in learner content. Currency remains MXN unless the business contract changes. |
| P0 / 2 | Reproducible local onboarding | A fresh-clone walkthrough with one start command, health checks for all services, synthetic demo account, clear port-conflict handling and owned-process shutdown. Measure download/setup separately from startup. |
| P0 / 3 | Teaching and visual polish | Consistent terminology, larger evidence details, purposeful diagrams, readable code, keyboard navigation and chapter links. Re-capture changed demonstrations and regenerate affected lessons; review actual exported files. |
| P1 / 4 | Risk-based regression workflow | Versioned route inventory and risk register; requirement-to-case-to-test-to-result traceability; explicit P0 smoke selection; business assertions for each critical path. |
| P1 / 5 | Excel intake and test authoring | A validated workbook schema, row-level errors, duplicate-ID handling, normalized JSON and a reviewed mapping to actual UI/API contracts. Generated cases compile, execute and retain original case IDs. |
| P1 / 6 | Reproducible reporting and CI | Root-level CI configuration, machine-readable results, useful HTML summary, traces on failure, and links to actual hosted runs. Compare results only for the same commit, app variant and browser configuration. |
| P2 / 7 | Advanced distributed exercises | Measured delayed projection, controlled dependency failure, conflicting replay, authorization boundaries and a concurrent idempotency exercise with a defined contract. Persistence/outbox durability is a separate extension, not a claim about the current in-memory app. |

Keep a separate commit for each coherent change. Use a release candidate for the English revision, then a final release only after application, code examples, videos and documentation agree. Video replacements belong to the same release as the application behavior they demonstrate.

## Proposed application experience

Use the included **TransferLab** as the immediate test application. The new launcher starts its three services and creates a usable synthetic account without installing the test runners. See [QUICKSTART.md](QUICKSTART.md).

For the next revision, add an English training dashboard with a scenario selector, a clear reset action for the learner's own account, transaction history, and visible correlation between the canonical transfer and the ledger projection. Keep the core exercise small enough for the two-hour workshop. Put concurrency, durability and fault injection in explicitly labeled extensions.

Do not add a database merely for appearance. Add persistence only if the exercise needs to prove restart recovery or durable delivery, and test those guarantees explicitly. Keep the existing lightweight in-memory mode available for fast onboarding.

## Critical paths and acceptance criteria

| Path | Risk | Required evidence |
|---|---|---|
| Sign in and open an owned account | Unauthenticated or cross-account access | Authenticated access succeeds; missing session is rejected; a second fixture cannot access the first fixture's real account. |
| Successful transfer | Incorrect debit or missing record | Starting balance 100000 minor units, transfer 10000, final balance 90000, exactly one canonical record and the same visible reference. |
| Insufficient funds | Rejected request changes state | Attempt 110000, rejection, balance still 100000, no transfer record. |
| Sequential idempotent replay | Duplicate debit | Same key and body return the same transfer ID; one debit and one record. This does not prove concurrency behavior. |
| Conflicting replay | Key reused for a different intent | Same key with a different amount is rejected without a second effect. |
| Delayed ledger projection | UI success mistaken for downstream completion | Read-only polling for the exact returned ID; bounded deadline; compare business values. |
| Controlled unavailable dependency | False confidence from a mocked response | Separate UI error-presentation tests from integrated service-failure tests; check that the former has no backend mutation. |
| Hybrid browser and terminal | Unrelated records compared | Pass the exact browser transfer reference to TNZ and compare reference, status, amount, currency, source and balance. |

## Coverage model

Maintain separate metrics. A passing test count is not coverage.

1. **Requirement coverage:** requirements linked to reviewed tests / all approved in-scope requirements. Also show unassessed requirements.
2. **Critical-path coverage:** approved critical paths with the required assertions and latest execution evidence / all approved critical paths. Designed, automated, executed and passed are separate stages.
3. **Risk-weighted evidence coverage:** sum of agreed risk weights for risks with the required current evidence / total agreed in-scope risk weight. Publish the risk register and denominator; do not invent weights after seeing results.
4. **Execution status:** passed, failed, flaky, skipped, blocked and not run, with commit, environment, browser and timestamp.
5. **Code coverage:** report only when instrumentation actually ran. Browser coverage is not backend coverage, and API route discovery is not branch coverage. Playwright's browser coverage API is Chromium-specific. [Playwright coverage documentation](https://playwright.dev/docs/api/class-coverage).

Use HTML plus JSON/JUnit outputs for review and aggregation. Playwright Test supports multiple reporters; Java and Python retain their own runner configuration. [Playwright reporters](https://playwright.dev/docs/test-reporters).

## Excel-to-Playwright workflow

Use [test-cases-template.xlsx](../templates/test-cases-template.xlsx) and prompts P07–P09 in the [prompt pack](PROMPTS.md).

Inventory workbook sheets and columns first. Normalize rows into structured cases while preserving workbook, sheet, row and case ID. Validate preconditions, concrete expected results, data types and repeated steps. Treat formulas, macros, external links and cell instructions as data to review, not commands to execute. Do not silently discard hidden rows or ambiguous cases.

Then map actions to verified locators/API endpoints and existing fixtures. Unsupported manual assertions and missing business rules remain blocked. Generate a small representative batch, review it, compile it, and run it before converting the rest. Preserve a conversion report; an Excel row is not automatically an executable or passing test.

The template is supplied now. A general-purpose importer and conversion of the user's own workbook remain future work because no workbook has been supplied. For `.xlsx` processing, explicitly choose whether to read formula text or stored values; cached values can be stale. [openpyxl tutorial](https://openpyxl.readthedocs.io/en/stable/tutorial.html).

## Release gates

- The English UI, all three language examples, documentation and visible video demonstrations agree.
- Each test owns and cleans up its server data and browser context. Retries do not conceal failures.
- P0 paths have reviewed business assertions and current results; blocked cases and exclusions are visible.
- All twelve videos remain within the agreed 6–8 minute range after edits; changed episodes have new hashes and sampled visual reviews.
- The normal lab passes; the intentional defect exercise still fails for the documented reason.
- CI claims include an actual run link. A local result never becomes a hosted result merely because a workflow file exists.
- New learner-facing material uses English, readable layouts and the approved blue/gray/white palette.

# Executed verification: distributed TransferLab

Verified locally on 2026-09-09. These are real local executions, not predicted results.

| Item | Observed value |
|---|---|
| Runtime | Node.js 24.16.0; npm 11.13.0 |
| Test library | @playwright/test 1.63.0, package-lock.json installed |
| Browser | Microsoft Edge 152.0.4191.66, fresh headless test contexts |
| Healthy final execution | 10 passed, 0 failed, 0 skipped, 0 flaky; 1 worker; retries 0 |
| Final run timestamp | 2026-09-09T19:12:34.230Z |
| Runner duration | 13.61168 seconds |
| Healthy command | `npm test`, with `TEST_HOOK_KEY` set |
| Defect execution | 1 failed as intended, exit code 1; no skipped tests |
| Defect run timestamp | 2026-09-09T19:12:18.682Z |
| Defect runner duration | 4.033606 seconds |
| Defect command | `npm test -- --grep TR-03`, BASE_URL port 3100, ARTIFACT_DIR evidence/defect |
| Cleanup after final suite | Gateway hook stats: fixtures 0, operations 0 |
| Retained artifacts | 10 healthy traces and browser videos; healthy screenshots; defect trace, video, screenshot, error context and business-state attachment |

The healthy suite validates UI success and rejection, canonical balance/record invariants, sequential idempotency, three invalid amounts, a browser-only service-error mock, an independent ledger projection, lookup schema, idempotency conflict and actual cross-fixture authorization. Every fixture teardown checks session revocation.

The defect run activates `LAB_DEFECT_DUPLICATE=1` only in separate services on ports 3100/3101/3102. TR-03 fails at `tests/regression.spec.ts:54` because the repeated request returns a different transfer ID. The attached business-state JSON confirms the deeper defect: `balanceMinor:80000`, `total:2`. The defective service processes were stopped after capture; the healthy service processes remained on 3000/3001/3002.

Inspect [healthy HTML report](html-report/index.html), [healthy JSON](results.json), [healthy JUnit XML](results.xml), and [defect HTML report](defect/html-report/index.html). The happy-path screenshot was visually inspected: confirmation, MXN 900.00 balance, labeled form and all three service roles are visible with no clipping at 1440 x 960.

This establishes the local classroom behavior. It does not establish production banking correctness, durable distributed transactions, concurrent retry guarantees, a real mainframe integration or a Java suite execution. Python and TNZ evidence lives in the adjacent mainframe folder.

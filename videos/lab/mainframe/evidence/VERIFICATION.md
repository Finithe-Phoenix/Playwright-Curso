# Mainframe classroom laboratory execution evidence

Executed locally on 2026-09-09. These results concern the working laboratory; they do not assert that any real mainframe was contacted.

| Executed suite | Result | Evidence |
|---|---|---|
| Python real TN3270 protocol tests | 5 passed | `terminal-tests.xml`, `offline-terminal.txt`, `backend-unavailable-terminal.txt` |
| Python Playwright core browser/API regressions, including the tnz hybrid | 3 passed | `python-core-plugin-tests.xml`, `hybrid-python-result.json`, `python-tr02-result.json`, `python-tr03-result.json`, screenshots and traces |
| Java Playwright + JUnit core regressions, including the tnz bridge | 3 passed, 0 failures, 0 errors, 0 skipped | `hybrid-java-tests.xml`, `core-java-tests.xml`, `hybrid-java-result.json`, `java-tr02-result.json`, `java-tr03-result.json`, screenshots and traces |
| TypeScript Playwright Test + Python tnz bridge | 1 passed | `hybrid-typescript-tests.xml`, `hybrid-typescript-result.json`, `hybrid-typescript-browser.png`, `hybrid-typescript-terminal.txt`, `ts-test-results` |

Total: **12 distinct passing cases**: five Python protocol tests; three Python browser/API cases; three Java browser/API cases; one TypeScript hybrid case. The three language suites each include one browser-to-terminal hybrid. Python's core suite with plugin-managed tracing took 13.39 seconds and its final five protocol tests took 2.97 seconds. Java's three-case Maven run took 22.114 seconds, with 10.64 seconds in CoreRegressionTest and 4.846 seconds in HybridTransferTest. TypeScript's runner reported 4.5 seconds. Installation/download time is excluded. `verification.json` aggregates only these non-overlapping reports.

The protocol tests verify a successful reference lookup through an actual `tnz` TCP session, an unknown reference, invalid input rejection, an explicitly bounded screen wait that times out, and an unavailable upstream producing the explicit BACKEND UNAVAILABLE screen. Their upstream business data and outage are deterministic fixtures. The simulator and IBM client are real running components in those tests.

Each hybrid test created an isolated fixture with a starting balance of 100000 minor units, authenticated its own browser context, filled the accessible transfer form with 100.00 MXN, clicked Transferir, checked the UI status and 900.00 MXN balance, read the unique transfer reference, invoked `adapter.py` in a separate Python process, and checked the terminal's exact reference, COMPLETED status, 10000 minor units, MXN currency, source account and 90000 minor-unit balance. The `simulated: true` marker was also asserted. Cleanup ran in `finally`.

The extra Python and Java core cases use the actual gateway and browser/API. TR02 submits 1100.00 MXN against 1000.00 MXN, matching the course contract; it verifies HTTP 422 with INSUFFICIENT_FUNDS, the visible error, the unchanged 100000 minor-unit balance and zero transfer records. TR03 sends the same body and idempotency key twice sequentially, verifies HTTP 201 then 200 with identical response data and ID, one transfer record and a single debit to 90000 minor units. These are separate business regressions, not terminal negative tests.

TR02 was aligned from the initial boundary example to the course's exact 1100.00 amount after the primary core runs. The affected Python and Java cases were rerun and passed individually; see `python-tr02-contract-tests.xml` (5.15 seconds) and `java-tr02-contract-tests.xml` (7.477 seconds test time). These repeated cases are excluded from the distinct-case total.

The exact Python command with `--tracing retain-on-failure` passed all three core cases after the hybrid example was changed to respect plugin ownership. A subsequent default-tracing check passed seven then-existing cases in 8.75 seconds and retained the manual teaching trace; the fifth protocol case was subsequently validated with the complete five-case protocol suite. That intermediate check remains in `python-all-tests.xml` and is excluded from the unique-case total. Both Python and Java now attempt fixture deletion even if trace finalization fails.

Post-run `/__test/stats` reported **0 fixtures and 0 operations**, saved in `cleanup-status.json`. The terminal readiness command subsequently returned `{"status":"READY","simulated":true}`. The terminal simulator remains available on loopback port 2323; its startup record is `simulator.stdout.log`. The gateway and two distributed services are managed by the sibling laboratory.

Verified versions: Python 3.12.10; IBM tnz 0.6.6; ebcdic 2.0.1; pytest 8.4.2; pytest-playwright 0.7.1; Playwright Python and Java 1.62.0; TypeScript Playwright Test 1.63.0; JDK 11.0.17; Maven 3.9.11; Node 24.16.0; Microsoft Edge 152.0.4191.66. All browser runs used the installed Edge channel. The default Chromium setup is documented but a newly downloaded Chromium was not used in these executions.

The Java Maven project uses the official optional Node-bundle exclusion and `PLAYWRIGHT_NODEJS_PATH` to reuse the local Node installation. It retains the matching Playwright Java driver. Python's package consistency check found no broken requirements. PowerShell setup/start files passed syntax parsing; Python files compiled without syntax errors.

The combined Python run emits one upstream tnz deprecation warning about Python's event-loop discovery; it did not fail a test. The TypeScript runner emitted a console-color environment warning; it did not fail a test.

Scope limits: the simulator reads the same authoritative in-memory account store through the gateway. It does not independently reconcile a z/OS ledger, prove mainframe persistence, emulate CICS, or test TLS to a real host. The TLS configuration in the README was checked against IBM documentation and installed source; it was not executed against a real host. Screenshots and traces contain only the synthetic laboratory data.

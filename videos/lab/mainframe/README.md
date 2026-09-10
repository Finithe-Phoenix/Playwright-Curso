# Local Playwright + IBM tnz laboratory

This folder implements a working **TN3270 classroom simulator**, the real IBM `tnz` Python client, and hybrid Playwright tests. No mainframe account, z/OS image, CICS license, real customer record, or credentials are required.

The browser submits a synthetic transfer to the distributed application. The test obtains its reference, enters that reference into a real 3270 input field through `tnz`, presses Enter, and asserts the returned amount, currency, source account, status and balance. The terminal server reads the gateway's `/__test/lookup` endpoint. That endpoint reads the same authoritative **in-memory account data** used by the application. This demonstrates cross-protocol automation and correlation; it does not provide an independent z/OS reconciliation or durable storage proof. The distributed laboratory separately exercises its eventually consistent ledger projection.

## Architecture

```text
Playwright browser ---- HTTP ----> Gateway :3000 ----> Accounts :3001
       |                                  |
       | reference                        | GET /__test/lookup?reference=...
       v                                  ^
Python IBM tnz ---- TN3270 ----> Classroom simulator :2323

Accounts outbox ---- HTTP events ----> Ledger projection :3002
```

All classroom services bind to loopback. The simulator implements Telnet binary, terminal type and end-of-record negotiation plus a minimal 3270 Erase/Write, field, cursor, and Enter flow. It is deliberately a small training protocol implementation, not a general mainframe emulator.

## Prerequisites and installation

Install Python 3.12 for the provided Windows scripts. The Java path additionally needs a JDK 11 or later and Maven 3.9. The distributed laboratory needs Node.js as specified in its sibling README. Reserve ports 3000, 3001, 3002 and 2323.

From this folder in PowerShell:

```powershell
# Terminal-only dependencies (small installation).
.\setup.ps1

# Add Python Playwright + pytest and Chromium before the class.
.\setup.ps1 -Browser
```

Manual equivalent, also useful on Linux or macOS with `python3` and `.venv/bin/python`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-browser.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

The tested dependencies are pinned in the two requirements files. Installation needs internet; the completed exercises use local services. Corporate package mirrors and browser download rules may require preparation before class.

## Start the exercise

First start the sibling distributed application according to its README, with `TEST_HOOK_KEY` set to the same local classroom key used by tests. In a second PowerShell terminal, run:

```powershell
Set-Location 'C:\Users\daedg\OneDrive\Documentos\HSBC\Playwright\work\videos\lab\mainframe'
.\start.ps1
```

This terminal intentionally stays occupied until Ctrl+C stops the simulator. In another terminal check readiness:

```powershell
.\.venv\Scripts\python.exe adapter.py health --timeout 5
# Expected JSON: {"status":"READY","simulated":true}
```

Health is verified through a real `tnz` session and the expected 3270 screen, not just an open TCP port. The terminal can be ready even when the distributed gateway is stopped; lookup then returns `BACKEND UNAVAILABLE`.

## Run Python tests

The five standalone protocol tests start a server on a temporary loopback port and use the real IBM `tnz` client over a real socket. Their upstream business data and outage come from deterministic fixtures; no other service is necessary. They cover success, unknown reference, invalid input, a bounded screen timeout, and an unavailable backend.

```powershell
.\.venv\Scripts\python.exe -m pytest test_terminal.py -q --junitxml=evidence\terminal-tests.xml
```

The hybrid test creates an isolated fixture, authenticates the browser through its context request client, performs a real browser transfer, asserts the terminal result, captures evidence, and deletes the fixture in `finally`.

```powershell
$env:TEST_HOOK_KEY = 'classroom-demo-only'
.\.venv\Scripts\python.exe -m pytest test_hybrid_browser.py -q --junitxml=evidence\hybrid-python-tests.xml

# Optional, when Microsoft Edge is already installed:
.\.venv\Scripts\python.exe -m pytest test_hybrid_browser.py -q --browser-channel msedge

# Three core regressions: success + terminal, insufficient funds, sequential retry.
.\.venv\Scripts\python.exe -m pytest test_hybrid_browser.py test_core_regression.py -q --browser-channel msedge --tracing retain-on-failure
```

Open the saved trace locally:

```powershell
.\.venv\Scripts\python.exe -m playwright show-trace evidence\hybrid-python-trace.zip
```

When `--tracing` is enabled, the pytest plugin owns tracing and retains files according to that option. With tracing off, the hybrid example saves its explicit teaching trace in `evidence/hybrid-python-trace.zip`. Fixture deletion runs even if explicit trace finalization fails. `pytest.ini` provides a default base URL for examples using relative paths.

The subprocess boundary deliberately gives `tnz` ownership of its own event loop. The same CLI works from Python, TypeScript and Java. It avoids mixing `tnz`'s event loop with the Playwright runner's loop.

## Run Java + JUnit

The runnable implementations are `java/src/test/java/training/HybridTransferTest.java` and `java/src/test/java/training/CoreRegressionTest.java`. `mvn test` executes three cases: successful transfer with terminal verification, insufficient funds without mutation, and a sequential idempotent retry with one debit and one transfer record.

```powershell
Set-Location .\java
$env:TEST_HOOK_KEY = 'classroom-demo-only'
$env:PLAYWRIGHT_NODEJS_PATH = (Get-Command node).Source
mvn exec:java '-Dexec.mainClass=com.microsoft.playwright.CLI' '-Dexec.args=install chromium'
$env:PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = '1'
mvn test

# Optional existing Edge instead of the downloaded Chromium:
$env:PW_BROWSER_CHANNEL = 'msedge'
mvn test
```

The Maven file excludes the optional all-platform Node bundle and reuses the Node executable already required by the distributed lab through `PLAYWRIGHT_NODEJS_PATH`. Playwright still supplies its matching 1.62.0 driver. Set `TNZ_PYTHON` only if the Python virtual environment is elsewhere. The test defaults to the sibling mainframe `.venv` and passes arguments through `ProcessBuilder`, without composing a shell command. The Java test verifies the same six business values as the Python test. JUnit XML appears in `java/target/surefire-reports`; browser and terminal evidence appears in `evidence`.

## Run TypeScript + Playwright Test

This test reuses the sibling distributed laboratory's installed `@playwright/test` package. Install that laboratory first; no second npm dependency tree is needed. From the mainframe folder:

```powershell
$env:TEST_HOOK_KEY = 'classroom-demo-only'
node ..\distributed\node_modules\@playwright\test\cli.js test --config typescript\playwright.config.ts

# Optional existing Edge:
$env:PW_BROWSER_CHANNEL = 'msedge'
node ..\distributed\node_modules\@playwright\test\cli.js test --config typescript\playwright.config.ts
```

`typescript/hybrid.spec.ts` invokes the same Python adapter using `execFile` and an array of arguments. It checks the same transfer values, writes a browser screenshot and terminal snapshot, and cleans its fixture in `finally`. The report is `evidence/hybrid-typescript-tests.xml`; Playwright traces are under `evidence/ts-test-results`.

## Read the terminal directly

Replace the example reference with one from a transfer whose fixture is still present:

```powershell
.\.venv\Scripts\python.exe adapter.py lookup TRANSFER_REFERENCE --timeout 8 --snapshot evidence\terminal.txt
```

The command prints one JSON object. Exit code 0 means `READY` or `COMPLETED`; 2 means a business result such as `NOT FOUND` or `BACKEND UNAVAILABLE`; 1 means validation, connection or timeout failure. A removed fixture's reference must no longer resolve.

The adapter's verified public API sequence is:

```python
from adapter import TerminalSession

with TerminalSession(timeout=8) as session:
    result = session.lookup(reference)
    assert result["status"] == "COMPLETED"
    assert result["reference"] == reference
```

Internally it uses the actual IBM API: `tnz.Tnz`, `connect`, `scrstr`, `wait`, `key_home`, `key_eraseeof`, `key_data`, `enter`, and `shutdown`. The screen wait uses a monotonic deadline, incoming data processing, a screen predicate and keyboard-unlocked checks. The adapter rejects references outside 1–48 ASCII letters, digits, underscores or hyphens.

## How this changes with a real authorized mainframe

Playwright controls a browser or HTTP API. IBM `tnz` controls a 3270 session. A real hybrid test needs an approved test host, application-specific panel identifiers, actual screen fields, isolated test records, timeouts derived from that system, and verified TLS. Those items cannot be validated with this simulator.

For a separately approved real-host implementation, the IBM configuration for certificate and hostname verification is:

```python
import os
from tnz import tnz

os.environ["SESSION_SSL_VERIFY"] = "hostname"
terminal = tnz.Tnz("AUTHORIZED-TEST")
terminal.connect(
    host=os.environ["MAINFRAME_HOST"],
    port=int(os.environ.get("MAINFRAME_PORT", "992")),
    secure=True,
    verifycert=True,
)
# Pump terminal.wait(...) with a deadline and implement the actual host's panels.
# The classroom adapter intentionally rejects non-loopback plaintext connections.
```

This configuration snippet was checked against IBM documentation and the installed package; no real host or TLS session was available for execution. Never adapt the simulator's `secure=False` setting to a remote host. Real screen dumps and browser traces can contain credentials or customer data; use the synthetic laboratory artifacts when demonstrating AI prompts.

## Copy-and-paste AI prompt

```text
Act as a senior Playwright and IBM tnz test engineer. Use only the attached
adapter.py, simulator.py, test_hybrid_browser.py, and distributed API contract.
Create one regression for a UI transfer followed by a 3270 lookup of the exact
same transfer reference. Use Python pytest, TypeScript Playwright Test, or
Java JUnit as selected below. Invoke the existing adapter CLI using exact
argument arrays, an 8-second terminal deadline and a 12-second subprocess limit.
Create an isolated synthetic fixture; share browser authentication through the
browser context's request client; assert accessible UI status, exact reference,
COMPLETED, integer amountMinor, currency, sourceAccountId and balanceMinor.
Capture sanitized evidence and delete the fixture in finally. Do not invent
tnz methods, host credentials, screen selectors or API endpoints. Clearly label
the terminal as a local TN3270 simulator using the SAME in-memory account data.
Add a negative case for an unknown reference. Return files, execution commands,
assumptions, and separate verified results from steps requiring execution.
Selected language: [Python / TypeScript / Java]
```

## Primary sources

- [IBM tnz repository and overview](https://github.com/IBM/tnz)
- [IBM tnz API reference](https://ibm.github.io/tnz/tnz/)
- [IBM certificate and hostname verification](https://ibm.github.io/tnz/security/)
- [Playwright Python installation and pytest integration](https://playwright.dev/python/docs/intro)
- [Playwright Java installation and Maven integration](https://playwright.dev/java/docs/intro)

See `evidence/VERIFICATION.md` for executed results and the distinction between the protocol tests and the cross-service browser tests.

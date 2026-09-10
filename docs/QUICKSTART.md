# Start the local test application

## Application only

Install Node.js 22 or later, clone the repository, then run:

```powershell
git clone https://github.com/Finithe-Phoenix/Playwright-Curso.git
cd Playwright-Curso
node scripts/start-demo.mjs
```

Open **http://127.0.0.1:3300/transfers**. The terminal prints a synthetic demo username and password. Use them in the login form. No database, Docker installation, npm installation or external account is required to run the application itself.

The three local processes use ports 3300, 3301 and 3302. Choose a different group with `node scripts/start-demo.mjs --port=3500`. An occupied port stops startup; the launcher does not take over or stop an existing service. Keep the terminal open; Ctrl+C stops the demo's own processes and discards its in-memory data.

The baseline UI still has Spanish labels; its coordinated English migration is phase 1 of the [improvement plan](IMPROVEMENT-PLAN.md). New instructions and the launcher output are English. This launcher does not start the optional TN3270 simulator; follow the [mainframe lab instructions](../videos/lab/mainframe/README.md) for that extension.

## Try the workflow manually

1. Sign in with the credentials printed by this launch.
2. Confirm an opening balance of MXN 1,000.00.
3. Transfer MXN 100.00 to the supplied beneficiary.
4. Confirm MXN 900.00 and retain the displayed transfer reference.
5. Restart the demo to begin with fresh in-memory data.

The demo account is for exploration. Automated tests create separate fixtures; never hard-code its random credentials or account IDs into tests.

## Verify startup and core API behavior

With ports 3400–3402 free:

```powershell
node scripts/start-demo.mjs --verify --port=3400
```

This check starts all services, verifies HTML delivery, sign-in, transfer, sequential replay, canonical balance/record, ledger projection and cleanup, then stops its services. A failure returns a nonzero exit code. It is an API/startup smoke check, not browser automation or a replacement for the regression suite.

## Run the existing TypeScript regression suite

Keep the demo launcher running. In a second PowerShell terminal, from the clone root:

```powershell
cd videos/lab/distributed
npm ci
npx playwright install chromium
$env:PW_CHANNEL = 'chromium'
$env:BASE_URL = 'http://127.0.0.1:3300'
$env:TEST_HOOK_KEY = 'classroom-demo-only'
$env:ARTIFACT_DIR = 'local-results'
npm test
npx playwright show-report local-results/html-report
```

For a visible happy-path run, replace `npm test` with `npm test -- --grep TR-01 --headed`. The initial browser download needs network access. The new `local-results` folder keeps your run separate from the preserved baseline evidence. Use the Python/Java instructions in the mainframe folder for their own environments and runners.

## Prompts and spreadsheet cases

Start with P00 in [PROMPTS.md](PROMPTS.md), then use P01–P06 for discovery, coverage, implementation and reporting. Use P07–P09 for Excel intake, mapping and generation. The [Excel template](../templates/test-cases-template.xlsx) contains three synthetic example cases; it is not a converted user workbook.

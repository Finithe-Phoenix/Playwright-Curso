# TransferLab: distributed Playwright classroom

This folder is a working local teaching simulator. It is not an HSBC application or a production banking implementation. It uses synthetic identities, beneficiaries and money. All state lives in memory and disappears when the processes restart.

## Start on Windows

Requirements: Node.js 22+ and an installed Microsoft Edge, or a Playwright Chromium download. The package lock pins Playwright Test 1.63.0. The default test configuration opens a fresh headless Edge test context; it does not reuse personal browser profiles.

```powershell
Set-Location -LiteralPath 'C:\Users\daedg\OneDrive\Documentos\HSBC\Playwright\work\videos\lab\distributed'
npm ci
npx playwright install ffmpeg
$env:TEST_HOOK_KEY = 'classroom-demo-only'
npm run start:lab
```

The recorder needs Playwright's own FFmpeg package even when the browser is an already installed Edge. `npx playwright install ffmpeg` installs that small runtime dependency; a system FFmpeg executable used for video production is separate. Installing Playwright Chromium also installs the recorder dependency. Complete this download before class. If you extract the course into another folder, replace the example absolute path with your actual `videos\lab\distributed` directory.

The sample hook key is a public, synthetic classroom value, not a credential for any external system. The server requires a key in the environment. It must match the test terminal. All services bind to 127.0.0.1. The startup script checks ports first and fails if another application is using them. Stop this laboratory by pressing Ctrl+C in its own terminal.

In another terminal:

```powershell
Set-Location -LiteralPath 'C:\Users\daedg\OneDrive\Documentos\HSBC\Playwright\work\videos\lab\distributed'
$env:TEST_HOOK_KEY = 'classroom-demo-only'
npm test
npm run report
```

For an installed Playwright browser instead of Edge:

```powershell
npx playwright install chromium
$env:PW_CHANNEL = 'chromium'
npm test
```

This switches only the test browser, not the web application. To show the happy path during class, run `npm test -- --grep TR-01 --headed`. Keep installation outside the two-hour lesson.

## Actual architecture and consistency

```text
Browser / TypeScript / Java / Python
              |
      gateway :3000 (HTML, session, routing)
              |
      accounts :3001 (authoritative account, transfers, outbox)
              |
      ledger :3002 (polls outbox every 250 ms, independent projection)
```

The account debit, canonical transfer record and outbox event change together in one synchronous critical section inside a single Node process. This is an educational representation of a transactional outbox. It has no durable database, crash recovery, broker or multi-node transaction. Production durability and concurrent distributed failure handling are outside the simulator's guarantees.

`GET /api/transfers` reads the immediate canonical state from the accounts process, preserving the course contract. `GET /api/ledger/transfers` reads the independent projection, which may lag. TR-06 polls the exact transfer ID with a 5-second deadline; a timeout fails the test. UI auto-waiting cannot establish that another service has processed a business event.

Deleting a fixture removes its account, transfer records, idempotency entries and browser sessions and removes its ledger projection. The in-memory outbox retains event history until restart; this is a small classroom event log, not sensitive-data retention guidance.

## API and UI contract

Base URL: `http://127.0.0.1:3000`. `/health` identifies each process as `environment:test`, `contractVersion:1`. The gateway health endpoint establishes its own process readiness; the startup coordinator verifies all three service health endpoints separately.

| Route | Purpose |
|---|---|
| `POST /__test/fixtures` | Header `X-Test-Hook-Key`; body `{runId,caseId,currency:"MXN",balanceMinor:100000}`; returns 201 `{fixtureId,username,password,sourceAccountId,beneficiaryId}`. |
| `POST /api/session` | Body `{username,password}`; returns 200 and a 30-minute HttpOnly SameSite=Lax cookie. Use the browser context's request client. |
| `GET /api/accounts/{id}` | Authenticated canonical balance, integer `balanceMinor`. |
| `POST /api/transfers` | Authenticated; header `Idempotency-Key`; body `{sourceAccountId,beneficiaryId,currency:"MXN",amountMinor:10000}`. First 201, sequential identical replay 200 and identical object; conflicting body 409. |
| `GET /api/transfers?sourceAccountId=...` | Authenticated immediate `{items,total}` from accounts. |
| `GET /api/ledger/transfers?sourceAccountId=...` | Authenticated eventual `{items,total,projectionCursor}` from ledger. |
| `GET /__test/lookup?reference=...` | Local synthetic read-only bridge for TN3270 simulator; returns `{reference,status,amountMinor,currency,sourceAccountId,balanceMinor}` or 404. |
| `DELETE /__test/fixtures/{fixtureId}` | Hook header; returns 204, repeated deletion also 204. |
| `GET /__test/stats` | Hook header; account fixture and idempotency entry counts, useful for cleanup evidence. |

`/transfers` also offers a manual login form using the synthetic fixture credentials. UI labels are the original Spanish contract: `Cuenta origen`, `Beneficiario`, `Importe (MXN)`, button `Transferir`. English video narration explains them. The success role is `status`; rejections use `alert`. Test ID `account-balance` shows `MXN 900.00` after one 10000-minor-unit transfer from 100000.

## Included meaningful tests

| Test | Evidence |
|---|---|
| TR-01 | UI success plus 90000 canonical balance and exactly one matching transfer. |
| TR-02 | UI rejection, 422 `INSUFFICIENT_FUNDS`, unchanged 100000 balance and zero records. |
| TR-03 | Same key and body twice, 201 then 200, identical result ID, only one debit; UI reload balance. Sequential replay does not demonstrate concurrency behavior. |
| TR-04, three cases | API rejects 0, negative and fractional minor-unit amounts with zero effects. |
| TR-05 | Browser-route 503 mock tests only error presentation/button recovery and verifies no backend mutation. |
| TR-06 | Exact returned transfer reaches separate ledger process within deadline; validates mainframe lookup response. |
| TR-07 | Reusing one key with a different amount returns 409 and no second debit. |
| TR-08 | Requests without session 401; access to another fixture's real account and beneficiary returns 403. |

Each test has its own fixture and Playwright context. Preparation uses a separate HTTP context; the hook header never becomes a browser-wide header. Login uses `page.request` so its session is shared with the page. Teardown attaches observable business state, deletes its specific fixture and checks session revocation. All requests have bounded runner timeouts; retries are 0.

For the recorded lessons, all traces/screenshots/videos are retained in `evidence/test-results`; HTML, JSON and JUnit reporters write under `evidence`. These contain synthetic test credentials and the public classroom hook value; use approved redaction and retention rules before adapting evidence capture to real environments. Results in `evidence/VERIFICATION.md` describe only commands actually run.

## Controlled defect exercise

The accounts service includes an explicitly opt-in `LAB_DEFECT_DUPLICATE=1` switch. It reproduces a repeated-debit defect while retaining 200 on the second request. The correctly written TR-03 fails because IDs, balances and records disagree. This is a teaching variant, disabled in the ordinary startup.

To run the defective variant concurrently with the healthy classroom, use dedicated ports in a separate terminal:

```powershell
$env:TEST_HOOK_KEY = 'classroom-demo-only'
$env:PORT = '3100'
$env:ACCOUNTS_PORT = '3101'
$env:LEDGER_PORT = '3102'
$env:LAB_DEFECT_DUPLICATE = '1'
npm run start:lab
```

And from a separate test terminal:

```powershell
$env:TEST_HOOK_KEY = 'classroom-demo-only'
$env:BASE_URL = 'http://127.0.0.1:3100'
$env:ARTIFACT_DIR = 'evidence/defect'
npm test -- --grep TR-03
```

Expected outcome: one failing test and a nonzero exit code. Keep its failure evidence; do not change the assertion to 80000 and do not add retries or skips to make it green. Close only the defective laboratory terminal after the exercise.

Official Playwright sources checked for the implementation:

- [API testing and browser-context session sharing](https://playwright.dev/docs/api-testing)
- [Fixtures and teardown](https://playwright.dev/docs/test-fixtures)
- [Web assertions and expect.poll](https://playwright.dev/docs/test-assertions)
- [MicrosoftEdge and Chromium channels](https://playwright.dev/docs/browsers)

The Java and Python teaching routes use their own runners. This TypeScript folder does not assert that Maven JUnit or pytest tests were executed. The adjacent `mainframe` folder owns Python TNZ and browser-terminal integration evidence.

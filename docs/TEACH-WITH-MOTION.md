# Teach the two-hour workshop with the motion edition

Use the complete lessons as companion material. In the live workshop, play selected chapters, pause at the business assertion, and let learners reproduce the behavior on their own machines. Each learner chooses one primary language; compare the other two implementations afterward.

## Live agenda — 120 minutes

| Minutes | Activity | Observable outcome |
|---|---|---|
| 00–10 | Watch the 2:36 walkthrough; map the browser, services and terminal | Learner explains each automation boundary |
| 10–25 | Discover critical paths with prompts P00–P03 | Risk register and requirements-to-tests matrix |
| 25–50 | Generate and execute one complete case in the chosen language | A passing case with an isolated fixture and meaningful assertions |
| 50–65 | Add insufficient funds and replay checks | Negative behavior and exactly-once effects are verified |
| 65–80 | Follow the exact transfer reference through services | Canonical state and delayed projection are distinguished |
| 80–100 | Run the local TNZ extension | Browser and terminal evidence agree on the same reference |
| 100–115 | Inspect an intentional idempotency failure | Learner diagnoses the defect without weakening assertions |
| 115–120 | Produce a concise regression report | Execution status, evidence and remaining gaps are explicit |

## Clip → question → action

| Lesson / chapter | Ask before resuming | Learner action |
|---|---|---|
| Walkthrough / Write the contract | What evidence does this prompt require? | Copy and adapt P00 and P04 |
| 02 / Use the accessible contract | What makes this locator stable? | Inspect the real label and use an exact locator |
| 02 / Build insufficient funds separately | Which state must remain unchanged? | Assert the balance and canonical record count |
| 05 / Place cleanup after evidence | What belongs to this test? | Inspect owned fixture teardown |
| 06 / Poll only the observation | Which endpoint may be safely polled? | Bound a read-only projection query |
| 07 / Exercise the user action once | What did the browser interception bypass? | Label the result as a mocked UI experiment |
| 08 / Protect the monetary oracle | Would this assertion detect a duplicate debit? | Inspect the observed balance and identity mismatch |
| 11 / Assert every business value | Which reference ties the interfaces together? | Compare exact reference, amount, currency and balance |
| 12 / Write a defensible regression report | Which cases actually ran? | Link executed cases to their evidence |

The player includes chapter buttons, a focus mode and native full-screen controls. Keep code and terminal demonstrations full screen when projecting in a classroom.

## Reproduce the browser example in TypeScript

Start the application from the repository root:

```powershell
node scripts/start-demo.mjs
```

In a second terminal, from the repository root:

```powershell
cd videos/lab/distributed
npm ci
npx playwright install chromium
$env:PW_CHANNEL = 'chromium'
$env:BASE_URL = 'http://127.0.0.1:3300'
$env:TEST_HOOK_KEY = 'classroom-demo-only'
$env:ARTIFACT_DIR = 'local-results/classroom'
npx playwright test --grep 'TR-0[123]'
npx playwright show-report local-results/classroom/html-report
```

These commands execute three cases with fresh synthetic fixtures. The video records a previous local run; learners must inspect their own exit code and report before calling their run successful. Use the documented Python or Java project for those tracks instead of mixing runner APIs.

## Prompt to pair with the demonstration

```text
Inspect this Playwright-Curso checkout and the running local application at http://127.0.0.1:3300. Use TypeScript and the existing Playwright Test fixtures unless I select the Python or Java track.

Implement one complete transfer regression. Reuse an isolated owned fixture. Inspect the actual application labels and API contract before choosing locators. Submit a 10000-minor-unit transfer from an opening balance of 100000. Assert the visible result, canonical balance of 90000, one canonical transfer and the exact returned transaction ID. Clean up only this test's fixture.

Show the proposed patch, explain each assertion, then run the case if execution tools are available. Save new artifacts under local-results. Do not invent a passing result, replace business assertions with visibility checks, add fixed sleeps, or use retries to conceal a defect. Report any unresolved assumptions explicitly.
```

For workbook intake, use P07–P09 in [the full prompt pack](PROMPTS.md). The Excel template contains synthetic examples to review, not a conversion of a learner's real workbook. Expected results and source-row mappings require review before automatic generation.

## Evidence boundaries

The captured 503 is a browser interception. The terminal is a local simulator. The code and prompt panels are explanatory animation, while the browser footage and displayed run observations come from actual local executions. Use these distinctions when asking learners what each test proves.

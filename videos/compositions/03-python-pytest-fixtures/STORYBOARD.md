# Episode 03: Python: Fixtures That Own Their Data

## Frame 1

status: animated
src: compositions/s0301.html
start: 0.000
duration: 38.234
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Translate the lifecycle

Now implement the same business cases in Python with pytest and the synchronous Playwright API. The important translation is the lifecycle, not replacing camel case with underscores. Each case must receive fresh data, authenticate its own browser context, execute its assertions, and release resources even when something fails. The pytest plugin already provides a page and context. Build your laboratory fixtures around those objects so isolation and trace options remain understandable. Keep the same amounts, record counts, and idempotency rules.

## Frame 2

status: animated
src: compositions/s0302.html
start: 38.234
duration: 34.250
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Confirm one Python environment

Open the Python test project and invoke the virtual environment's interpreter directly. Check the installed packages against the project's requirements, then run pytest with a targeted case selection. Calling Python as a module launcher ensures pytest comes from this environment. If your terminal finds a different Python on its search path, packages and browsers can appear to be missing even though another environment contains them. Resolve that mismatch first, and record the interpreter used so another learner can reproduce your execution.

## Frame 3

status: animated
src: compositions/s0303.html
start: 72.484
duration: 37.994
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Separate two HTTP responsibilities

Draw two HTTP clients beside the browser. A dedicated preparation client uses the local test hook key to create and remove fixtures. The page's associated request client logs in and queries business APIs as the simulated user. Keep the hook header away from global browser headers. This prevents a business request from accidentally carrying administrative test capabilities. It also makes failures easier to classify: fixture creation, login, transfer submission, and observation have different expected responses and different evidence requirements.

## Frame 4

status: animated
src: compositions/s0304.html
start: 110.478
duration: 36.482
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Use a yielding fixture

A function-scoped fixture can yield the created dataset to a test and finalize it afterward. The displayed skeleton explains ownership rather than providing a complete implementation: create data through the documented local endpoint, yield its identifiers, and delete that exact fixture in the finalization block. Your actual helper must check response statuses and handle partial setup failures. If login fails after creation, cleanup still owns the created fixture. Avoid a global reset that erases data belonging to another learner or parallel worker.

## Frame 5

status: animated
src: compositions/s0305.html
start: 146.960
duration: 35.930
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Authenticate the provided context

Use the context supplied by the pytest plugin and post the fixture's synthetic credentials through its associated request client. Assert the successful status before navigating. Because this request belongs to the browser context, the resulting cookie becomes available to the page. An independently created HTTP client has separate cookie storage unless you deliberately transfer state. Keep this choice visible in the fixture instead of hiding it in a utility with unclear ownership. Always identify whose session the browser is actually using.

## Frame 6

status: animated
src: compositions/s0306.html
start: 182.890
duration: 40.418
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Write the visible behavior

Inside the successful transfer test, navigate and select the fixture's account and beneficiary before entering one hundred pesos. The excerpt focuses on submission once those selections exist. Python's synchronous API does not require JavaScript await expressions. Use Playwright's expectation object for UI assertions so the intended text condition can settle. A plain immediate text comparison has different waiting behavior. When asking AI to translate the test, require the synchronous API throughout; mixing synchronous and asynchronous patterns produces failures unrelated to the business rule.

## Frame 7

status: animated
src: compositions/s0307.html
start: 223.308
duration: 35.882
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Check response semantics

Observe the account using the authenticated page request client. In Python, the response status in this example is a property, while parsing JSON uses a method. These small language differences are easy for generated code to get wrong. Assert the successful HTTP status, then the integer balance. Apply the same pattern to the canonical transfer collection and inspect its count and fields. For the separate distributed ledger view, use bounded polling rather than assuming that its record appears immediately after account settlement.

## Frame 8

status: animated
src: compositions/s0308.html
start: 259.190
duration: 37.994
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Capture the rejection response

For insufficient funds, prepare eleven hundred pesos in a fresh fixture. Enter the response expectation context before clicking, and match the transfer request specifically. After the context closes, inspect the captured response, its business error code, and the UI alert. Then prove the balance and transfer count stayed unchanged. This distinguishes a business rejection from a button that never submitted anything. A locator timeout, a network failure, and an insufficient funds response are different observations and should not become one generic rejection result.

## Frame 9

status: animated
src: compositions/s0309.html
start: 297.184
duration: 36.074
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Keep idempotency outside variation

Create the request body and idempotency key once within the Python case, then submit the same values twice through the authenticated context. Check creation followed by replay, compare the identifiers, and assert one debit and one record. If you parameterize cases later, keep the fixture function-scoped so each parameter receives independent data. A parameter list describes inputs; it does not automatically isolate the state those inputs mutate. Inspect resulting test names so failures identify the business case and dataset used.

## Frame 10

status: animated
src: compositions/s0310.html
start: 333.258
duration: 35.018
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Retain a useful trace

Run the Python suite with trace retention on failure and request a JUnit XML result file. The plugin's trace options apply to its managed fixtures; a browser context created manually in a helper needs its own trace management. That is why we extended the provided fixtures. Inspect an actual failed run to confirm the trace exists and can be opened. A configuration line expresses intended behavior, while a saved artifact demonstrates that it occurred. Keep those statements separate in your execution report.

## Frame 11

status: animated
src: compositions/s0311.html
start: 368.276
duration: 38.354
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Preserve the original failure

Review fixture finalization after a deliberately failing assertion. Cleanup should attempt to remove only the owned dataset and release its preparation client. If cleanup also fails, report that problem with the fixture identifier without replacing the original assertion failure. Save evidence before destroying the context or deleting data needed for inspection. For an interrupted process, record outstanding fixture identifiers so a later recovery step can target them. Reliable teardown belongs to the experiment's design, rather than being a cosmetic action after the assertions finish.

## Frame 12

status: animated
src: compositions/s0312.html
start: 406.630
duration: 36.650
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Explain your fixture graph

Finish by drawing the dependency graph for one Python test. The preparation client creates the dataset; the dataset and browser context establish authentication; the page performs the action; API observations verify effects; finalizers release what they own. Point to the code that guarantees each transition. Then report the actual status of the three cases, including blocked setup or remaining failures. You now have a Python structure that preserves the TypeScript version's business meaning while using pytest's own lifecycle and reporting conventions.

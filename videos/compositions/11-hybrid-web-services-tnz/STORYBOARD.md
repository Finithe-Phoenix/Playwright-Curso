# Episode 11: Hybrid Regression: One Correlation Across Interfaces

## Frame 1

status: animated
src: compositions/s1101.html
start: 0.000
duration: 40.634
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Follow one transfer across interfaces

Build the hybrid regression around one transfer reference. The browser submits a real request to the local services, the test obtains its canonical identifier, and the TNZ adapter enters that identifier into the simulated terminal. The final assertions compare the business values across those observations. This is orchestration across browser, HTTP, subprocess, and terminal protocol boundaries. The terminal still reads the same in-memory account data. Keep that limitation visible while demonstrating the additional field interaction and correlation behavior that the hybrid test actually exercises.

## Frame 2

status: animated
src: compositions/s1102.html
start: 40.634
duration: 35.330
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Prepare an isolated hybrid fixture

Create a new synthetic fixture for the hybrid case and preserve its cleanup identifier. Send the hook header only on the preparation request, then authenticate through the browser context's request client using the returned credentials. Check both response statuses before navigating. The test owns the fixture until terminal assertions and evidence capture finish. If you delete the data immediately after the browser action, the later terminal lookup will correctly return not found. Lifecycle ordering is part of the hybrid scenario's correctness.

## Frame 3

status: animated
src: compositions/s1103.html
start: 75.964
duration: 36.242
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Perform the actual browser transfer

Select the fixture's source account and beneficiary, enter one hundred pesos, and click the transfer button. Assert the visible confirmation and the resulting balance. This step must use the running local application, with no route substitution for the central hybrid case. The excerpt starts after selecting account and beneficiary. A screenshot can illustrate the page, but the test result comes from the assertions and subsequent service observations. Preserve both the browser evidence and the identifiers needed to continue into the terminal boundary.

## Frame 4

status: animated
src: compositions/s1104.html
start: 112.206
duration: 38.234
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Extract the canonical correlation

Read the canonical transfer collection filtered by the fixture's source account. Confirm the response is successful and that exactly one record exists before selecting its identifier. This makes the lookup unambiguous within the isolated case. The working example obtains the identifier from this canonical collection; capturing it directly from the submission response is another valid approach when that response is already observed. Never use a hardcoded example reference or a global latest-record query. The terminal must inspect the operation created by this exact browser execution.

## Frame 5

status: animated
src: compositions/s1105.html
start: 150.440
duration: 36.386
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Call the adapter from Python

Invoke the adapter in a dedicated Python subprocess with an argument list. The terminal deadline is eight seconds, and the outer process call has a twelve-second timeout. Keeping TNZ in its own process gives its event loop clear ownership and avoids mixing it with the browser runner. Capture output, inspect the exit status, then parse the JSON. The executable should come from the prepared terminal environment. Do not assemble a shell command from the reference; exact arguments preserve its value and keep execution behavior predictable.

## Frame 6

status: animated
src: compositions/s1106.html
start: 186.826
duration: 37.514
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Call the same boundary from TypeScript

The TypeScript version uses Node's executable-file operation, wrapped as a promise, to call the same Python adapter. Pass the script path, action, reference, and timeout as separate arguments. The process timeout is measured in milliseconds in this API, unlike Python's seconds. Keep that unit difference visible when reviewing generated code. The working Windows example also hides the helper window. A rejected process call or invalid JSON fails the hybrid step; it must not be converted into an empty object followed by skipped assertions.

## Frame 7

status: animated
src: compositions/s1107.html
start: 224.340
duration: 36.434
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Call the same boundary from Java

The Java version passes the executable and arguments through ProcessBuilder, then waits with a bounded timeout. If the child process exceeds that limit, terminate it and fail the test with a clear cause. After completion, inspect its exit value and parse the structured output using the project's JSON library. Keep process lifecycle separate from browser lifecycle so cleanup can address either failure. The excerpt shows invocation and its deadline; the complete source also reads output and asserts the returned business values before finalizing the fixture.

## Frame 8

status: animated
src: compositions/s1108.html
start: 260.774
duration: 38.618
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Assert every business value

Compare the terminal result with the exact reference, completed status, source account, currency, amount, and expected balance. Also require the simulated flag so the report retains the environment's identity. A matching amount alone could describe another transfer, while a matching reference alone would not reveal incorrect numeric parsing or stale balance presentation. These checks combine identity and business content. They demonstrate agreement with shared local account data under this scenario, not an independent reconciliation against a real mainframe database or durable ledger storage system.

## Frame 9

status: animated
src: compositions/s1109.html
start: 299.392
duration: 35.738
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Keep ledger projection as another check

If the capstone includes the asynchronous ledger projection, query its separate endpoint using the same source account and transfer identifier. Apply the bounded read-only polling rule from the distributed episode. Do not assume the terminal lookup proves projection completion, because the simulator reads authoritative accounts data directly. Your evidence matrix should contain a separate row for canonical state, projected ledger state, and terminal presentation. That distinction lets a failure identify which observation was missing instead of merging unrelated checks.

## Frame 10

status: animated
src: compositions/s1110.html
start: 335.130
duration: 38.378
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Capture evidence before cleanup

Save the browser screenshot, trace, terminal snapshot, and structured comparison result while the fixture still exists. Keep their names associated with the current case and attempt. Then close the terminal process or session, finish trace capture, and delete only the owned fixture. Inspect cleanup results without erasing the original failure. The supplied examples demonstrate the sequence; before scaling to many concurrent attempts, give artifacts unique names too. Independent account data does not prevent two tests from overwriting a shared evidence filename in the same directory.

## Frame 11

status: animated
src: compositions/s1111.html
start: 373.508
duration: 34.850
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Add a meaningful negative case

Add a separate lookup case for an unknown reference, or query a reference after its fixture has been deleted. The expected result is not found, rather than completed with empty fields. Keep this test separate so its data lifecycle is obvious. Also distinguish a terminal timeout from a business not-found response. Review the adapter's exit-code contract and structured status together. This negative coverage demonstrates that your orchestration rejects missing business evidence instead of accepting any screen that happens to arrive.

## Frame 12

status: animated
src: compositions/s1112.html
start: 408.358
duration: 36.242
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Review the hybrid checkpoint

Your checkpoint is one executed hybrid case in the language you selected, plus linked evidence for the browser action and terminal comparison. Explain how the reference moved between tools, how both timeout layers are bounded, and why the terminal view is not an independent data authority. If you also ran the projection check, show its separate result. Keep Java, Python, and TypeScript outcomes distinct rather than assuming translation guarantees execution. Next, assemble reusable AI prompts, a capstone regression plan, and a defensible report.

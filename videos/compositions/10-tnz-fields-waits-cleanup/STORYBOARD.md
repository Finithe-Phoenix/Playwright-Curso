# Episode 10: TNZ Sessions: Fields, Waits and Cleanup

## Frame 1

status: animated
src: compositions/s1001.html
start: 0.000
duration: 34.730
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Build a predictable terminal session

Inspect the adapter that turns terminal interaction into a predictable test boundary. We will connect, wait for the correct panel, enter a transfer reference, parse the result, and close the session. Each step has a specific condition and a bounded lifetime. The public laboratory wrapper is named TerminalSession; it is our adapter, not an IBM library class. Its implementation uses real TNZ methods, so you can inspect the difference between application-specific screen logic and the underlying protocol client.

## Frame 2

status: animated
src: compositions/s1002.html
start: 34.730
duration: 37.946
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Create the actual TNZ client

Open the adapter source and find the TNZ object creation. One object represents this terminal connection. The adapter selects the character encoding used by the local simulator, so screen bytes become the intended text. A browser page and a terminal screen do not share a locator model or character buffer. Keep this conversion visible when diagnosing unexpected symbols or missing labels. The displayed initialization is an excerpt from the adapter; connection, bounded waiting, and cleanup belong to the following lifecycle rather than being optional additions.

## Frame 3

status: animated
src: compositions/s1003.html
start: 72.676
duration: 37.658
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Connect within the local boundary

The adapter connects to loopback on the simulator's terminal port. Its host validation rejects nonlocal addresses before attempting this plaintext classroom connection. The secure flag shown here describes only that local setup; certificate verification has no effect when the connection is unencrypted. After connecting, the adapter immediately waits for the expected initial panel. A successful socket call is not enough to begin typing. If setup fails after connection, the session owner must still shut down the partially established connection before reporting the original error.

## Frame 4

status: animated
src: compositions/s1004.html
start: 110.334
duration: 36.290
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Use a monotonic deadline

Inspect the wait helper. It computes a deadline from a monotonic clock, reads the current screen, and processes incoming terminal events in short bounded increments. Repeating a screen read without processing events may keep observing stale content. The helper also checks whether the session disconnected and saves a timeout snapshot before raising an error. This is application-level waiting around the TNZ event method. The deadline expresses how long this local operation may take, and prevents a missing panel from hanging the test process indefinitely.

## Frame 5

status: animated
src: compositions/s1005.html
start: 146.624
duration: 34.250
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Require a ready keyboard too

The wait helper does not accept matching text alone. It also checks the terminal's program-wait and system-lock conditions before returning control to the caller. This prevents the test from typing while the displayed panel is still not ready for input. Treat those conditions as part of the adapter's readiness contract. If the label appears but input remains locked, inspect the terminal exchange and timeout evidence. Do not bypass the lock check merely because a screenshot looks complete; presentation and readiness can be different states.

## Frame 6

status: animated
src: compositions/s1006.html
start: 180.874
duration: 34.226
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Validate and enter the reference

Before touching the field, validate the reference against the adapter's allowed length and characters. The local field accepts one to forty-eight ASCII letters, digits, underscores, or hyphens. Then move to the input field with the home key, erase its previous contents, and type the reference through TNZ. Clearing matters when a new reference is shorter than the old one; otherwise, stale characters can remain and select the wrong lookup value. This field sequence belongs to our panel and must be reviewed for any different application.

## Frame 7

status: animated
src: compositions/s1007.html
start: 215.100
duration: 33.602
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Wait for the submitted reference

After Enter, wait for a result screen containing the submitted reference and a status that is no longer the initial ready state. A generic completed message could belong to a previous lookup. Correlation therefore belongs in the screen predicate itself, before parsing amounts or declaring success. The helper still requires an unlocked terminal and a deadline. If the server returns not found or backend unavailable, the screen can be a valid response even though the business operation did not produce a successful lookup result.

## Frame 8

status: animated
src: compositions/s1008.html
start: 248.702
duration: 36.146
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Parse the labeled business values

The adapter extracts values from labeled result lines and returns a structured object. For a completed lookup, it converts amount and balance into integers and preserves currency, source account, status, and reference. The hybrid test compares those values with the transfer it created; parsing is insufficient. Missing labels or invalid numbers should surface as errors rather than becoming empty strings or zeros that happen to satisfy a weak assertion. Review the parser alongside the actual screen contract whenever a field name or layout changes.

## Frame 9

status: animated
src: compositions/s1009.html
start: 284.848
duration: 34.826
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Preserve screen evidence

Use the adapter's snapshot option to save the observed panels. The resulting text connects readiness and result states with named steps. Pair this snapshot with the structured JSON output so a reviewer can inspect both the parsed values and their source screen. The placeholder reference in the displayed command must be replaced with a real transfer identifier whose fixture still exists. Do not present the placeholder as a successful lookup. If the fixture was already deleted, a not-found result is the meaningful expected behavior.

## Frame 10

status: animated
src: compositions/s1010.html
start: 319.674
duration: 37.562
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Always release the connection

The session wrapper closes the TNZ connection on exit, including after a parsing or assertion failure. Its setup path also closes if the initial panel never becomes ready. Inspect both paths, because a finalization block around only the test body cannot clean up a resource that failed earlier during entry. The underlying close operation uses TNZ shutdown. Capture necessary screen evidence before releasing the session, and preserve the original failure if a secondary cleanup problem appears. Ownership should remain understandable across test cases.

## Frame 11

status: animated
src: compositions/s1011.html
start: 357.236
duration: 38.258
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Test negative terminal outcomes

Run the terminal protocol tests for successful lookup, unknown reference, unavailable backend, invalid input, and a missing-screen timeout. These checks distinguish business data, missing records, dependency errors, validation, and bounded waiting. Inspect each actual result independently. The adapter's exit code of two represents a business response; code one represents an operational or validation failure. Interpret the structured status too. Treating every nonzero result as identical loses the information needed to diagnose a hybrid workflow efficiently.

## Frame 12

status: animated
src: compositions/s1012.html
start: 395.494
duration: 38.906
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Explain the adapter contract

Your checkpoint is an explanation of the adapter's full contract: permitted reference input, loopback destination, ready-screen condition, field operations, result predicate, structured values, timeout behavior, and cleanup. Point to the implementation and one actual snapshot. Then explain why matching the reference matters before accepting a completed status. Call the adapter from a browser test without embedding terminal details everywhere. The next episode uses that boundary from Python and Java to compare the same synthetic transfer across web, service, and terminal observations.

# Episode 06: Distributed Workflows: Correlation and Polling

## Frame 1

status: animated
src: compositions/s0601.html
start: 0.000
duration: 34.658
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Observe a distributed business event

A browser assertion cannot tell you when another service has processed a business event. Follow one transfer from the gateway to authoritative account state and then into a separate ledger projection. We will use the returned transfer identifier to connect those observations and apply a bounded wait only where the contract permits delay. The exercise runs across local processes. Its value is learning to distinguish business commitment, asynchronous visibility, and diagnostic evidence without assuming that a quiet browser network means everything finished.

## Frame 2

status: animated
src: compositions/s0602.html
start: 34.658
duration: 37.898
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Inspect the three processes

Start the distributed laboratory and inspect its architecture. The gateway serves the browser on port three thousand. Accounts holds balances, canonical transfers, and an event log on port three thousand one. Ledger runs separately on port three thousand two and polls that log to update its own projection. The startup coordinator checks all three services. A gateway health response alone describes the gateway process, so keep dependency readiness evidence separate. These boundaries let us reproduce timing differences without connecting to any external banking infrastructure.

## Frame 3

status: animated
src: compositions/s0603.html
start: 72.556
duration: 35.738
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Understand the local transaction

In this simulator, the debit, canonical transfer, and outgoing event are updated in one synchronous section of the accounts process. This illustrates an outbox: business state and the event describing it should not drift apart. However, the state is in memory. Restarting the process loses it, and there is no durable database or message broker. Describe the demonstrated guarantee precisely. A successful classroom run does not establish crash recovery, durable delivery, or transaction behavior across multiple production nodes.

## Frame 4

status: animated
src: compositions/s0604.html
start: 108.294
duration: 36.146
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Capture identity from the response

Submit the transfer once and capture the returned identifier from its successful response. Keep this identifier in the test's evidence object, together with the source account and expected amount. Do not search for the latest transfer across the whole system. Another test could create a newer record between your action and query. Correlation should follow the value produced by this exact operation. The same identifier will later travel into the terminal adapter, allowing the web, API, and terminal observations to refer to one synthetic transfer.

## Frame 5

status: animated
src: compositions/s0605.html
start: 144.440
duration: 36.482
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Assert commitment immediately

First query the authoritative account and canonical transfer collection through the gateway. These endpoints preserve the original laboratory contract: after the successful response, the balance is ninety thousand centavos and the transfer exists once. An incorrect authoritative balance is not an expected ledger delay. Fail that assertion and investigate it directly. This ordering keeps the test honest about which component owns each guarantee. It also prevents an overly generous polling loop from hiding a defect in a state transition that should already have completed.

## Frame 6

status: animated
src: compositions/s0606.html
start: 180.922
duration: 36.746
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Query the delayed projection

Now query the separate ledger endpoint, filtered by the source account. Its response contains the projected records and may also expose a projection cursor for diagnostics. Inspect the HTTP status before treating its body as business data. The endpoint is intentionally different from the canonical transfer collection, despite similar records. Write both paths explicitly in the evidence matrix. If you accidentally query the canonical endpoint twice, the test may look distributed while never observing whether the ledger process consumed the event at all.

## Frame 7

status: animated
src: compositions/s0607.html
start: 217.668
duration: 39.386
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Poll only the observation

Use a bounded polling assertion to repeat the read until the exact transfer identifier appears. The polling body must not submit another transfer. It observes progress without creating new business effects. The excerpt checks membership within a five-second classroom deadline; afterward, inspect the matching record's amount, currency, source, and count. This deadline is a laboratory expectation, not a claim about production performance. On timeout, preserve the last response and correlation identifier so the failure explains what was observed instead of reporting only that time elapsed.

## Frame 8

status: animated
src: compositions/s0608.html
start: 257.054
duration: 35.282
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Do not replace progress with sleep

Compare polling with a fixed sleep. A fixed pause always waits the full duration, yet still fails if publication takes slightly longer. Polling can finish as soon as its business condition holds and produces a defined failure when the deadline expires. Browser locator waiting solves a different problem: it observes browser state, not the ledger process. Choose the wait according to the state you are observing. If publication is consistently slow, inspect service behavior and the expectation before increasing the timeout to hide failures.

## Frame 9

status: animated
src: compositions/s0609.html
start: 292.336
duration: 36.290
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Check duplicates after visibility

Once the projected transfer appears, inspect the filtered collection rather than stopping at membership. Verify its amount, currency, source account, and completed status, and ensure the expected single record count holds for this isolated fixture. In the replay case, correlate both responses to the same canonical identifier and inspect the projection for one business record. This demonstrates the simulator's observed behavior for that scenario. It does not prove every message-delivery failure mode, because the local event mechanism is deliberately limited.

## Frame 10

status: animated
src: compositions/s0610.html
start: 328.626
duration: 34.538
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Build a failure timeline

When the projection deadline expires, build a short timeline from the available evidence. Record the transfer response, authoritative balance, canonical record, ledger response, and process health observations with the same reference. Then form a hypothesis: the transfer may have committed while publication or consumption failed. Do not label that hypothesis as a confirmed root cause until logs or another observation support it. Use evidence to locate the broken boundary before asking AI to explain a distributed timeout.

## Frame 11

status: animated
src: compositions/s0611.html
start: 363.164
duration: 36.986
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Carry correlation into reporting

Attach a compact correlation summary to the test result. Include the case, fixture, transfer reference, expected amount, and paths used for authoritative and projected observations. Exclude credentials and unrelated account data. A reviewer should be able to move from a failed assertion to the matching service evidence without guessing which request mattered. The displayed structure is an example report shape, not proof of an executed result. Populate it with values captured during the actual attempt, and link the corresponding artifacts after the run completes.

## Frame 12

status: animated
src: compositions/s0612.html
start: 400.150
duration: 34.346
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

State the distributed evidence

Your distributed checkpoint should answer four questions. Did the account change correctly? Did the canonical transfer exist exactly once? Did that same identifier reach the separate projection within the classroom deadline? What evidence supports each answer? Keep any timeout or missing observation visible in the report. You now have a regression that crosses process boundaries while distinguishing commitment from delayed visibility. Next, a browser mock will help compare focused UI evidence with an integrated workflow.

# Episode 05: Isolation, Authentication and Test Data

## Frame 1

status: animated
src: compositions/s0501.html
start: 0.000
duration: 35.762
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Treat each test as an experiment

Reliable regression starts before the first click. In this episode, design an experiment whose starting data, identity, and cleanup belong to one test attempt. A new browser context removes browser state, but it does not reset money held by a backend service. Likewise, a fresh account does not remove cookies from a reused page. You need both boundaries. We will trace the fixture from creation to deletion and examine why retries, parallel workers, and authentication reuse can otherwise create misleading outcomes.

## Frame 2

status: animated
src: compositions/s0502.html
start: 35.762
duration: 37.394
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Create only the data you own

Use the local fixture endpoint to create a synthetic user, source account, and beneficiary with the agreed opening balance. Include a run identifier and case identifier for diagnosis. The server adds unique identifiers, so two learners can use the same case name without sharing mutable accounts. Inspect the creation status before reading the response. Retain the fixture identifier immediately, because cleanup needs it even when the next setup step fails. Never replace targeted fixture creation with a shared account that someone manually reset earlier.

## Frame 3

status: animated
src: compositions/s0503.html
start: 73.156
duration: 34.898
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Keep the hook client separate

The fixture client carries a capability used only by this local training environment. Configure its hook key from the laboratory environment and restrict its use to preparation and deletion requests. The business context authenticates using the synthetic credentials returned for its fixture. Do not install the hook header globally on the browser. This separation clarifies what each observation proves: ordinary business requests must work with the user's session, while setup endpoints deliberately create the data needed for a repeatable classroom experiment.

## Frame 4

status: animated
src: compositions/s0504.html
start: 108.054
duration: 38.426
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Authenticate where the page lives

Login through the HTTP client associated with the browser context. After a successful response, the session cookie is available to that context's page. Use the same loopback hostname for login and navigation; changing between localhost and its numeric address changes the cookie's host scope. When a page unexpectedly redirects to login, inspect that relationship before changing timeouts. Avoid saving synthetic session files unless a specific exercise requires them. Per-test login keeps identity ownership visible and is sufficient for this small local workflow.

## Frame 5

status: animated
src: compositions/s0505.html
start: 146.480
duration: 34.802
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Understand storage state reuse

Some suites save authenticated storage state to avoid repeating login. That can be appropriate when tests do not collide through the same user's server data, or when each worker receives its own account. Reusing a session file alone does not isolate account balances or transfer histories. Before adopting this optimization, list every mutable resource associated with that identity and decide who owns it. For our three central cases, fresh synthetic users are easier to reason about than a fast shared login followed by complicated repairs.

## Frame 6

status: animated
src: compositions/s0506.html
start: 181.282
duration: 37.226
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Give retries new data

A retry is another experiment, not a continuation that may reuse an already debited account. Arrange fixture setup so each attempt gets its own source account, beneficiary, session, and idempotency key. Within the idempotency case, reuse the key only for the two requests representing the same intended transfer. Across test attempts, generate a new intention and new data. Otherwise, a retry might succeed by replaying a transfer from the failed attempt, creating the appearance of stability while exercising a different path than the original test.

## Frame 7

status: animated
src: compositions/s0507.html
start: 218.508
duration: 36.650
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Verify ownership boundaries

Add an authorization extension after the three central cases: create two fixtures and try accessing one fixture's account with the other's session. The local contract defines a forbidden response for cross-fixture business access. Inspect both the response and the unchanged target state. This extension checks a different risk from insufficient funds. Keep it separately named and independently prepared so its purpose is clear. AI may suggest combining them for brevity, but a combined case often makes it harder to identify which rule actually failed.

## Frame 8

status: animated
src: compositions/s0508.html
start: 255.158
duration: 36.986
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Place cleanup after evidence

When a test fails, capture the relevant browser, API, and correlation evidence before deleting the fixture. Then close the browser context and remove only the owned data through the local deletion endpoint. Make the deletion operation idempotent so a second cleanup attempt is safe for that fixture. Record its response separately from the original failure. Deleting the entire laboratory state may appear convenient in a single demonstration, but it invalidates other running experiments and prevents meaningful parallel execution across learners or language versions.

## Frame 9

status: animated
src: compositions/s0509.html
start: 292.144
duration: 39.242
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Handle partial setup failures

Walk through a setup failure. Suppose fixture creation succeeds but authentication fails. The test body may never run, yet the created account still exists. The setup owner must therefore register cleanup as soon as creation succeeds, rather than waiting until every preparation step completes. Use the fixture mechanisms appropriate to your language and inspect their behavior during exceptions. If cleanup also fails, preserve the original cause and the remaining fixture identifier. A useful report explains both problems without converting either into a silently skipped success.

## Frame 10

status: animated
src: compositions/s0510.html
start: 331.386
duration: 39.530
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Add concurrency only after isolation

Now imagine two workers submitting transfers at the same time. Each owns a browser context and a separate fixture, so their account assertions remain deterministic. The shared local services can process both requests, but the observations remain filtered by each source account and transfer identifier. Increasing worker count changes scheduling, not the business oracle. If failures appear only under parallel execution, compare fixture identifiers and session ownership first. Then investigate service behavior with correlated evidence instead of immediately adding global locks around every test.

## Frame 11

status: animated
src: compositions/s0511.html
start: 370.916
duration: 35.954
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Ask AI to audit lifecycle edges

Give AI the setup and cleanup code together with the contract. Ask it to trace resource ownership through success, assertion failure, login failure, and an interrupted request. Require it to identify which fixture might remain and which evidence might be lost in each path. This is more useful than asking for generic best practices. Review every suggestion against the actual runner's lifecycle. If a proposed helper does not exist in your project, either implement it deliberately with clear responsibilities or reject that unsupported shortcut.

## Frame 12

status: animated
src: compositions/s0512.html
start: 406.870
duration: 32.738
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Produce an isolation checklist

Your checkpoint is a short ownership checklist attached to one executed case. It names the run, attempt, fixture, source account, browser context, and cleanup result. It also explains how authentication reached the page and where failure evidence was captured. Review the checklist with a partner and ask them to predict what happens if login fails or the test is retried. When those answers follow directly from the code, you have a solid foundation for the distributed observations in the next episode.

# Episode 07: Mocks and Real End-to-End Evidence

## Frame 1

status: animated
src: compositions/s0701.html
start: 0.000
duration: 33.026
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Choose the boundary deliberately

A mock is useful when its boundary matches the question you want to answer. This episode tests how the transfer page reacts to a temporary service error, then compares that evidence with the integrated cases already built. We will intercept one browser request and return a controlled response. That gives repeatable UI behavior without stopping services. It does not test whether the real backend generates that response during an outage. Write the scope beside the test name before implementing the route handler.

## Frame 2

status: animated
src: compositions/s0702.html
start: 33.026
duration: 34.106
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Read the error contract

The local error scenario uses status five hundred three with a service unavailable code and a documented Spanish message. The page should display that message in an alert and make the transfer button usable again. Because the browser interception prevents this submission from reaching the backend, the account should remain unchanged. These expectations describe our specific experiment. They do not describe every possible service failure; a real timeout after a committed debit requires a different test and a careful idempotency recovery design.

## Frame 3

status: animated
src: compositions/s0703.html
start: 67.132
duration: 35.282
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Prepare the state before mocking

Create a fresh fixture, authenticate its context, and select the source account and beneficiary. Confirm the opening balance before installing the response substitution. This separates setup failures from the error behavior under test. If your handler accidentally intercepts fixture creation or login, you are testing a different path. Keep the route match narrow enough to affect only transfer submission. The test should be able to explain exactly which request is controlled and which requests still communicate with the running local services.

## Frame 4

status: animated
src: compositions/s0704.html
start: 102.414
duration: 38.090
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Install a narrow route handler

Register the handler before clicking. Match the transfer route and check the request method inside the handler. Requests using other methods continue to the real server. For the POST, fulfill a JSON response with the agreed status, content type, code, and message. The excerpt uses an ordinary JavaScript object converted to JSON, so the browser receives the intended structure. A broad wildcard that replaces every request can make a page appear resilient while hiding broken account queries, authentication, or unrelated loading behavior.

## Frame 5

status: animated
src: compositions/s0705.html
start: 140.504
duration: 33.698
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Exercise the user action once

Enter one hundred pesos and click the transfer button once. Wait for the exact alert through a locator assertion, then verify that the button is enabled again. The visible error and recovery state are separate checks: a page might show the right message but leave the customer unable to try again. Keep the action count explicit. Repeated clicking could generate a different intention or obscure whether the UI recovered correctly from the controlled first response. The goal is a clear observation of one error transition.

## Frame 6

status: animated
src: compositions/s0706.html
start: 174.202
duration: 36.482
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Inspect real state after the mock

Query the authoritative account and canonical transfers using the authenticated API client. Verify the opening balance and an empty collection. This checks that your mocked browser submission did not create an unexpected backend effect. It also confirms you did not accidentally leave a real submission path active alongside the route handler. Explain the causal limit carefully: unchanged state follows because this request was intercepted before delivery. It does not prove a production service guarantees rollback whenever a customer receives a five hundred three response.

## Frame 7

status: animated
src: compositions/s0707.html
start: 210.684
duration: 32.378
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Remove the controlled boundary

Remove the route handler when the focused case ends, or let the isolated context close under the fixture's ownership. If you reuse a page within a larger scenario, unregister the exact handler before attempting a real transfer. Otherwise, the next operation may keep receiving the synthetic error and your diagnosis will point at the wrong service. Prefer a separate fixture for the mocked case. Each test then has a clearly defined environment and does not depend on cleanup from a previous scenario.

## Frame 8

status: animated
src: compositions/s0708.html
start: 243.062
duration: 36.554
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Compare two kinds of evidence

Place the mocked UI case beside the integrated successful transfer. In the first, the test supplies a controlled response and observes browser behavior. In the second, the browser calls real local services and the test verifies their resulting state. Both are useful, but they answer different questions. The mock provides a deterministic way to exercise an error presentation that might be difficult to trigger reliably. The integrated case checks compatibility across the implemented boundaries for its actual environment, data, and execution conditions.

## Frame 9

status: animated
src: compositions/s0709.html
start: 279.616
duration: 34.802
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Keep backend resilience separate

Suppose you want to test a genuine service interruption next. Define where the interruption occurs, what the authoritative system may already have committed, and how the client recovers the same intention. Use a separate controlled environment and fault scenario. Do not relabel the existing browser mock as a distributed outage test. A timeout after commitment can require looking up the original transfer rather than issuing a new one. Idempotency gives a foundation, but a complete recovery scenario needs its own contract and observations.

## Frame 10

status: animated
src: compositions/s0710.html
start: 314.418
duration: 36.266
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Review generated mocks carefully

Ask AI to review the route handler with the actual error contract. Require it to identify the intercepted method, URL, response shape, and assertions about the browser and backend. Then ask which guarantees remain untested. Reject a patch that returns success from the mock while claiming to validate real transfer settlement. Also inspect whether the handler remains installed after the case. This review turns AI into an assistant for checking test scope, rather than a generator of convenient responses that make every scenario look successful.

## Frame 11

status: animated
src: compositions/s0711.html
start: 350.684
duration: 38.354
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Label the report precisely

Name the result as a UI error-handling test with a browser-supplied response. Include the synthetic status and the actual observed alert, button state, and authoritative state checks. Keep its coverage separate from the core successful, rejected, and idempotent transfer cases. The displayed report labels describe categories, not a fabricated result. Populate the observation fields only after execution. When another team reads the regression summary, they should understand immediately that this case tested presentation and recovery controls without exercising a real service outage.

## Frame 12

status: animated
src: compositions/s0712.html
start: 389.038
duration: 35.426
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Choose the next useful test

Your checkpoint is an executed, isolated mock case and a short explanation of its limits. Demonstrate the alert, the recovered button, and the unchanged local account state, using actual evidence. Then name one separate integrated failure scenario you would add if the product required it, such as a lost response after commitment. This distinction prevents inflated coverage claims while preserving the value of deterministic UI tests. Next, use traces and a controlled implementation defect to diagnose failure without weakening assertions.

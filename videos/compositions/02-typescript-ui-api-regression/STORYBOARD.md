# Episode 02: TypeScript: Reliable UI and API Regression

## Frame 1

status: animated
src: compositions/s0201.html
start: 0.000
duration: 34.682
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Design the test around risk

Build the TypeScript version of our three regression cases. Begin with the prepared fixture, not a shared account you clicked through earlier. The fixture supplies an authenticated page, source account, and beneficiary. Read the test name as a business promise: a transfer of one hundred pesos reduces the correct account by one hundred pesos exactly once. Your UI steps exercise the customer path, while authenticated API queries verify the resulting state. Neither observation should silently replace the other.

## Frame 2

status: animated
src: compositions/s0202.html
start: 34.682
duration: 33.482
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Use the accessible contract

Navigate to the transfer page and select the fixture's source account and beneficiary by their exact accessible labels. Fill the amount using the documented decimal format. These locators communicate what a user is choosing rather than where a control happens to sit in the page structure. If a label no longer matches, inspect whether the application changed deliberately. Avoid replacing the locator with a positional selector simply to obtain a green run; that could operate on the wrong account without an obvious failure.

## Frame 3

status: animated
src: compositions/s0203.html
start: 68.164
duration: 34.802
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Observe the right request

When the response itself is part of your evidence, register the response waiter before clicking. Match both the HTTP method and the pathname, so an unrelated request cannot satisfy the waiter. Keep the response promise and await it after the click. This order avoids missing a fast response from a local server. The displayed predicate is deliberately narrow. If your gateway adds another relevant request, inspect the network evidence and update the predicate from that observation rather than introducing a general wait for all traffic.

## Frame 4

status: animated
src: compositions/s0204.html
start: 102.966
duration: 34.586
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Wait on the UI meaning

After submission, assert the exact confirmation and the visible balance using Playwright's locator assertions. These assertions wait for the relevant UI condition instead of taking a single immediate text snapshot. They do not remove the need to understand your application's consistency guarantees. The balance is an immediate account observation in this lab, so nine hundred pesos is the expected result. A confirmation message alone is weaker: it could appear even if the amount, account, or number of debits were wrong underneath the interface.

## Frame 5

status: animated
src: compositions/s0205.html
start: 137.552
duration: 37.418
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Verify the authoritative account

Query the source account through the page's associated request context. It shares the browser session, so the query represents the same authenticated identity that submitted the transfer. Assert the HTTP status before interpreting the JSON body. Then compare the integer balance with ninety thousand centavos. If the request fails with an authorization response, diagnose authentication or ownership instead of reporting a wrong balance. Also retain the account identifier with your evidence so a reviewer can see which account the assertion actually examined during this run.

## Frame 6

status: animated
src: compositions/s0206.html
start: 174.970
duration: 36.674
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Verify the transfer record

Read the canonical transfer collection filtered by the source account. This observation is immediate; the separate ledger read model uses bounded polling introduced later. Assert one item and a total of one, then compare its source account, beneficiary, currency, amount, and completed status. Capture the returned transfer identifier for correlation. Counting a record without inspecting its values can approve the wrong transfer. Conversely, finding a matching record without checking the total can miss an accidental second debit and duplicated business record.

## Frame 7

status: animated
src: compositions/s0207.html
start: 211.644
duration: 32.882
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Build insufficient funds separately

Create a fresh fixture for the insufficient funds case and fill eleven hundred pesos. Register the same targeted response waiter, click once, and verify the rejection status and business error code. Assert the exact alert in the browser. Then query the account and transfer collection: the balance must remain one hundred thousand centavos, and the collection must remain empty. This is a test of absence of side effects, so a correct error message is only the beginning of the evidence you need to collect.

## Frame 8

status: animated
src: compositions/s0208.html
start: 244.526
duration: 36.794
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Keep an idempotent intention

For the idempotency case, prepare one request body and one key before sending either request. Reuse both values for the second submission. The fixture must belong to this case alone, and the two requests are sequential. In the correct local contract, the first response creates the transfer and the second returns the existing transfer. Two independent browser clicks with newly generated keys represent different intentions, so they would not test this rule. Inspect the request construction carefully when reviewing an AI-generated implementation.

## Frame 9

status: animated
src: compositions/s0209.html
start: 281.320
duration: 35.978
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Compare identity and effects

Parse both responses and compare their transfer identifiers. Then perform the state checks: the source balance is ninety thousand centavos and there is exactly one transfer record with that identifier. Reload the page and verify the visible balance as a UI observation. Matching identifiers alone would not exclude an implementation that accidentally debits twice while returning the same identifier. State and identity therefore answer different questions. Keep both assertions, if AI suggests simplifying the case to make it shorter or faster.

## Frame 10

status: animated
src: compositions/s0210.html
start: 317.298
duration: 37.226
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Run with an honest outcome

Run the three cases in the supplied TypeScript project and inspect the actual report. During diagnosis, begin without retries so the first failure remains visible. A failed case is useful evidence when its assertion reflects the business contract. Read the test name, the expected and actual values, and the associated request or trace before editing code. If startup failed, report a preparation failure separately. Do not label generated tests as passed because they compile, or because a previous execution used another application build and dataset.

## Frame 11

status: animated
src: compositions/s0211.html
start: 354.524
duration: 36.602
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Review an AI patch

Give AI a focused review task: inspect these three tests for missing business assertions, shared mutable data, invented APIs, and waits that could hide a defect. Include the contract and a sanitized failure excerpt. Ask it to explain every suggested change and identify the evidence supporting that change. Review the patch before applying it. A useful suggestion may improve a locator or cleanup block; an unacceptable suggestion changes ninety thousand to eighty thousand merely because a defective implementation produced that value during an actual run.

## Frame 12

status: animated
src: compositions/s0212.html
start: 391.126
duration: 39.266
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Name what you proved

Your TypeScript checkpoint consists of three isolated cases, not simply three browser recordings. The successful case combines UI behavior with authoritative state. The insufficient funds case proves rejection without side effects. The repeated request case checks one intention, one identifier, one debit, and one record. Record the actual outcome for each case and link its evidence. If a case remains blocked or failing, say so explicitly. In the next episodes, we preserve these business promises while changing the language and lifecycle management around the tests.

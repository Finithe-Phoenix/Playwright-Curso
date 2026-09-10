# Episode 09: Local 3270 Architecture and TNZ Setup

## Frame 1

status: animated
src: compositions/s0901.html
start: 0.000
duration: 34.562
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Add a terminal protocol boundary

We now extend the workflow beyond the browser. The terminal exercises use IBM's real Python TNZ library to communicate over a socket with a small local TN3270 simulator. The simulator displays a synthetic transfer lookup screen and queries the same account data as our web application. This is practical cross-protocol automation, not a connection to a real mainframe. You will understand the boundary, install the prepared client environment, and verify terminal readiness through an actual screen exchange.

## Frame 2

status: animated
src: compositions/s0902.html
start: 34.562
duration: 36.650
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Separate browser and terminal control

Playwright controls the browser and its HTTP observations. TNZ controls the terminal session. The hybrid test coordinates both tools through a transfer reference. Trying to locate a terminal field with a browser locator would confuse two different interfaces, unless your actual application provided a browser-based terminal with its own separate contract. Our laboratory uses a protocol client directly. Keep the boundary visible in the architecture diagram so each failure points to the tool and connection that actually produced its evidence during the test run.

## Frame 3

status: animated
src: compositions/s0903.html
start: 71.212
duration: 36.746
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Understand what the simulator displays

The terminal screen reads a local lookup endpoint using the transfer reference. That endpoint returns the authoritative in-memory transfer and current account balance from the accounts service. It does not query an independent mainframe database, and it does not prove durable persistence. The distributed ledger projection remains a separate observation from the earlier episode. This distinction matters when describing coverage: the terminal exercise checks reference transport, field interaction, screen parsing, and agreement across interfaces that expose the same synthetic data source.

## Frame 4

status: animated
src: compositions/s0904.html
start: 107.958
duration: 39.026
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Read the folder structure

Open the mainframe laboratory directory beside the distributed project. The simulator file owns the server-side terminal behavior. The adapter file wraps the real TNZ client with a session lifecycle, bounded waits, input validation, and structured output. Terminal protocol tests exercise this boundary with deterministic data, while the hybrid browser test uses the running distributed services. Read the requirements files before installation. Their separation lets you install a small terminal-only environment or include the browser dependencies required for the complete hybrid exercise.

## Frame 5

status: animated
src: compositions/s0905.html
start: 146.984
duration: 37.586
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Install the prepared environment

Run the supplied setup script from the mainframe directory. Use the browser option when you plan to execute the Python hybrid case, because terminal-only setup does not provide every browser dependency. Installation downloads packages and, when requested, Chromium; the completed exercise communicates only with local services. Finish those downloads before the live workshop. If your approved environment already supplies Edge, use the documented browser-channel option in the test runner rather than assuming a Chromium executable exists just because a browser opens normally on your desktop.

## Frame 6

status: animated
src: compositions/s0906.html
start: 184.570
duration: 37.850
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Start services in their own terminals

First start the distributed application using its documented synthetic hook value. Then start the terminal simulator in a separate terminal from the mainframe directory. Its default address is loopback on port twenty-three twenty-three. Leave that terminal running while the adapter connects. If the port is already occupied, inspect the conflict instead of stopping an unrelated application. The laboratory startup and shutdown instructions target only its own processes. Keeping these terminals separate also makes it easier to identify which service reported a connection or lookup failure.

## Frame 7

status: animated
src: compositions/s0907.html
start: 222.420
duration: 34.826
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Check a real terminal screen

Run the adapter's health action with a bounded timeout. This check opens a TNZ session and waits for the expected screen, rather than treating an open TCP port as sufficient readiness. A ready terminal does not prove the gateway is available: the simulator can display its initial panel while business lookup remains unavailable. Record the health result and then verify the distributed services separately. When you later submit a reference, any backend-unavailable status belongs to a different stage from establishing the terminal connection itself.

## Frame 8

status: animated
src: compositions/s0908.html
start: 257.246
duration: 34.994
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Identify the input and result fields

Inspect the initial screen snapshot and find the transfer reference input. This local panel deliberately has one reference field and labeled result lines for status, amount, currency, source account, and balance. Those labels are part of the simulator's contract. They are not universal mainframe field names. In the next episode, we will inspect how the adapter positions the cursor, clears the input, enters the reference, and waits for a result associated with that exact value before parsing any business fields from the screen.

## Frame 9

status: animated
src: compositions/s0909.html
start: 292.240
duration: 36.818
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Try an unknown reference

Before creating a transfer, run a lookup using a valid reference that does not exist in the current dataset. The expected business result is not found. This is different from failing to connect or reaching a deadline without receiving a usable panel. Inspect the adapter's JSON output and exit status together. Its command-line contract distinguishes successful readiness or completion, business results such as not found, and operational failures. Preserving these categories makes a hybrid test report much more useful than a single generic terminal error.

## Frame 10

status: animated
src: compositions/s0910.html
start: 329.058
duration: 38.306
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Keep plaintext local to the simulator

The classroom adapter uses an unencrypted connection only to loopback and rejects nonlocal destinations. That is part of this simulator's design, not a template for connecting to an external host. An authorized real environment would need its own host, screen contract, test records, and verified transport configuration. None of those are established by this lesson. Keeping the local boundary explicit allows you to learn field automation and orchestration without suggesting that a successful synthetic lookup validates access, security, or behavior on an actual mainframe platform.

## Frame 11

status: animated
src: compositions/s0911.html
start: 367.364
duration: 36.242
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Run protocol tests independently

Execute the standalone terminal tests before the full hybrid path. These tests launch their own local server with deterministic fixture data and communicate through the actual TNZ library over a real socket. They help isolate connection, field, and status handling from browser or gateway issues. Inspect the actual test count and result file instead of assuming the suite passed because it exists. A successful protocol suite supports the adapter boundary; the browser-to-terminal workflow still requires its own run against the distributed application.

## Frame 12

status: animated
src: compositions/s0912.html
start: 403.606
duration: 36.170
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Confirm the architecture checkpoint

Explain the complete lookup path to a partner: TNZ sends a reference to the local simulator, which calls the gateway lookup endpoint and displays shared account data. Then show your actual readiness result and protocol test outcome. Identify which components were running and which were unnecessary for the standalone tests. If an installation or connection failed, keep that checkpoint unresolved. You are prepared for the next episode when you can distinguish terminal protocol behavior, business lookup behavior, and the limits of this deliberately simulated environment.

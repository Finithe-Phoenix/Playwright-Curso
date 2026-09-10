# Episode 01: Build the Local Test Architecture

## Frame 1

status: animated
src: compositions/s0101.html
start: 0.000
duration: 32.570
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Start with an outcome

Welcome to advanced Playwright with AI. We will build regression evidence around one fictional transfer, using TypeScript, Python, or Java. Later, that same transfer will cross several local services and appear on a simulated terminal. Choose one language for your practical work, and use the others to compare architecture. Before opening an editor, write the outcome you want to prove: one authorized transfer changes the correct balance exactly once and leaves a traceable business record.

## Frame 2

status: animated
src: compositions/s0102.html
start: 32.570
duration: 33.794
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Read the system map

Read the diagram from left to right. The browser calls the gateway on port three thousand. The gateway coordinates an accounts service and a ledger service. Accounts owns the immediate balance change; the ledger exposes a delayed read model in our distributed variation. A Python terminal adapter later connects to a local terminal simulator. These processes run on your workstation. They provide realistic automation boundaries, but they do not represent a production bank or a real mainframe installation.

## Frame 3

status: animated
src: compositions/s0103.html
start: 66.364
duration: 36.290
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Choose the right observation

Open the laboratory contract before installing anything. The account and canonical transfer queries describe immediate business state. The distributed extension adds a separate ledger query with eventual consistency while preserving the business amounts. Keep those endpoints distinct in your notes. Otherwise, you may mistake an expected publication delay for a product defect. Write down which endpoint is authoritative, which one is delayed, and which environment your test uses. This decision determines whether an assertion should run immediately or poll.

## Frame 4

status: animated
src: compositions/s0104.html
start: 102.654
duration: 37.418
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Prepare TypeScript

For TypeScript, work inside the supplied test project and inspect its package file and lockfile. Install exactly that dependency set with the clean installation command. Then install the browser expected by the pinned configuration. The laboratory may select an installed Edge channel for the measured run, while Chromium installation supports a separately configured Chromium project. These choices must match the runner configuration. Finally, record the tool version. Keep your approved package mirror configuration instead of changing registries during the lesson.

## Frame 5

status: animated
src: compositions/s0105.html
start: 140.072
duration: 36.914
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Prepare Python

For Python, create a virtual environment with the interpreter selected for the laboratory. Invoke its Python executable explicitly so package installation and test execution cannot accidentally use another Python installation. Install the pinned requirements file, then ask that same interpreter to install Chromium through Playwright. The pytest plugin will provide the page and context fixtures used later. Keep this environment separate from the terminal adapter environment when their dependency files differ; sharing an operating system does not require sharing every package.

## Frame 6

status: animated
src: compositions/s0106.html
start: 176.986
duration: 37.898
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Prepare Java

For Java, inspect the Maven project and confirm the JDK selected by your terminal. The project fixes Playwright, JUnit, and the build plugins it needs. Maven resolves those dependencies; the documented Playwright installation step provides the browser. These are separate from running JUnit tests. Keep classroom execution sequential initially, because a shared Playwright object is not an appropriate shortcut for parallel threads. If dependency resolution fails, solve the environment issue before interpreting any resulting message as a failed transfer regression.

## Frame 7

status: animated
src: compositions/s0107.html
start: 214.884
duration: 34.130
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Check local readiness

Start the local laboratory from the distributed project directory using its start script. Check the gateway health endpoint before opening the transfer page, and inspect the service output for startup errors. A page that renders a shell is not enough evidence that dependencies are ready. Confirm the documented environment metadata, then keep the services running for the exercise. Record the actual response you receive. The response shown in a slide is an expected example until your own request has completed successfully.

## Frame 8

status: animated
src: compositions/s0108.html
start: 249.014
duration: 36.938
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Express money precisely

Our API represents money as integer minor units. One thousand pesos is one hundred thousand centavos; the transfer amount of one hundred pesos is ten thousand centavos. The browser displays decimal currency, but server assertions use integers. Put these values beside each other before generating tests with AI. This prevents an attractive test from sending one hundred centavos while claiming to transfer one hundred pesos. Also assert the currency explicitly, because a numerically correct amount can still describe the wrong business operation.

## Frame 9

status: animated
src: compositions/s0109.html
start: 285.952
duration: 34.394
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Define the three cases

Create three rows in your evidence matrix. The successful transfer must leave a balance of nine hundred pesos and one record. The insufficient funds attempt requests eleven hundred pesos, keeps the opening balance unchanged, and creates no record. The idempotency case repeats the same request with the same key and must still produce one debit and one record. Give each row a fresh fixture. These are separate experiments, so a failed first case must never prevent another case from receiving its own opening state.

## Frame 10

status: animated
src: compositions/s0110.html
start: 320.346
duration: 36.866
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Separate tools from decisions

Ask AI to inspect the contract and list missing information before writing code. Provide the language, runner, exact UI labels, endpoints, and expected business values. The model may help organize fixtures or explain a failing assertion, but it cannot establish that a test ran merely by generating plausible output. Keep generated code, reviewed code, and executed results as separate states. When a selector or response field is unsupported by your evidence, stop that assumption and inspect the actual application or documented contract.

## Frame 11

status: animated
src: compositions/s0111.html
start: 357.212
duration: 32.978
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Make a first observable run

Now run a small browser check against the local page using your chosen runner. In the TypeScript excerpt, navigation opens the transfer route and the amount field assertion checks an actual accessible label. Authentication must already be supplied by the prepared fixture. This tiny check verifies the browser can reach the intended screen; it does not prove a transfer works. Save its outcome as a readiness checkpoint, then move on to business tests with clear starting data and the stronger assertions we have defined.

## Frame 12

status: animated
src: compositions/s0112.html
start: 390.190
duration: 32.810
motion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis

Check your preparation

Before continuing, explain the system aloud without naming a testing method. Identify who owns the balance, where the transfer record appears, and which process will later display terminal data. Confirm that your chosen language runs its own test runner, your browser is installed, and your local health check has an actual result. If any item is blocked, record the blocker instead of inventing a passing checkpoint. You are ready for the next episode when the environment and the business contract are both explicit.

# Reliable, low-cost test authoring

Read this when a new or changed test waits on time, spawns processes, touches
env/files/ports, is slow or flaky, or adds a test file. It is authoring guidance
for those cases, not a checklist, gate, pre-push scan or review item. A project or
host rule to run the smallest checks that can disprove the change wins over anything here.

## Control time instead of waiting
- Replace a fixed sleep with a signal the test can observe or release. Do not hide
  a sleep behind a bigger timeout, a retry or a platform skip.
- When real time must pass across processes, poll against a monotonic-clock
  deadline in milliseconds, not an attempt count. Example: a fake CLI blocks on a
  release file the test writes, while the test polls for the CLI's ready file
  until the deadline.
- Put every state the test asserts later into the poll condition.
- Let the test release a child's next stage (a file or pipe it writes), not a timer.
- After an async operation, wait for the state it produces, not for the call to return.
- Inside one process, shorten or advance time through a real production option with
  a production default, e.g. `deadlineMs = DEFAULT_DEADLINE_MS`.

## No wall-clock speed assertions
- Count operations, or pick an input that is catastrophically slow if the code
  regresses and assert only the result.

## Spawn less
- Test parsing and validation in-process.
- Keep real-subprocess tests few per file and aimed at exit code, signals and stdio.
- Start independent children together, not one after another.
- Reproduce a live or network-only bug with the smallest composition that runs
  safely offline; keep any live-only check narrow and opt-in.

## Isolation and restoration
- Point HOME, `XDG_*` and TMPDIR at a per-test temp directory so tests cannot touch
  the developer's live configuration.
- Restore env, clocks and mocks. Scoped fault injection at an OS or external
  boundary is fine when restored, e.g. `mock.patch.object(module.os, "lstat",
  side_effect=boom)`.
- Close handles and children before removing their temp directory.
- Bind to port 0 instead of a fixed port.
- Fix a flake by cleaning shared state; do not hide it by serializing.

## Diagnostics
- Assert stderr before the exit code of a child, or put stderr in the failure
  message, e.g. `assertEqual(r.returncode, 0, r.stderr)`.

## Table-driven cases
- Add a row to the existing table (for example, `subTest` over a list of cases);
  add a row only when the behavior differs.

## Flake triage
- Reproduce in the original order first; an order-only failure points to
  shared-state leakage.
- Separate fixture state, a missing completion signal and a product race.
- Fix the producer of the state, not the consumer.
- Pick rerun counts from the failure shape you reproduced; do not demand a fixed
  streak of passes.
- If a deletion caused the failure, read why it was deleted before restoring it.

## Reachability
- Make a new test file reachable from the real runner. Check the discovery pattern
  and any wrapper or CI job that selects tests, then confirm the new file actually runs.

## Cost
- For a test over about a second, name what takes the time; a long test should
  prove something a cheaper layer cannot. Timings are report facts, not a step.

## Source
Adapted from anomalyco/opencode at 28907e89c067fe1148758366929b43fa294ebcc3:
[AGENTS.md](https://github.com/anomalyco/opencode/blob/28907e89c067fe1148758366929b43fa294ebcc3/AGENTS.md) (Testing),
[unit-tests skill](https://github.com/anomalyco/opencode/blob/28907e89c067fe1148758366929b43fa294ebcc3/.opencode/skills/unit-tests/SKILL.md) and
[packages/app/AGENTS.md](https://github.com/anomalyco/opencode/blob/28907e89c067fe1148758366929b43fa294ebcc3/packages/app/AGENTS.md) (Tests); and from
[OpenClaw writing-tests.md](https://github.com/openclaw/openclaw/blob/3195fba90643c3897c538f2f6891c405331bee9c/docs/help/testing/writing-tests.md) (cost budget, flake triage).

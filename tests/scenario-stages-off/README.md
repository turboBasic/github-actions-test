# Scenario: stages switched off for a repo that lacks the tasks

## What it exercises

`python-ci.yml`'s `run-typecheck: false` and `run-tests: false`, in the situation they were added for.

This branch **deletes** the `typecheck` and `test` tasks from `mise.toml`. That is `opus-magnum`'s
actual shape — `docs/consumers.md` records that its `[tasks.*]` are all `make` wrappers, so it defines
neither task and needs both inputs.

## Why it is worth a branch

Passing `run-tests: false` in a repo that *has* a test task proves only that the `if:` works. It says
nothing about the case the input exists for: a repo where leaving the default would fail. Deleting the
tasks is what makes the test real.

## Expected result

`ci / CI` **passes**, having run checkout, `uv sync --locked` and `mise run lint` — and nothing else.
The Typecheck and Test steps report as skipped.

Flip either input back to its default on this branch and the job fails with a task that does not
exist. That failure is the thing `opus-magnum` would hit without these inputs.

## Do not merge

`main` defines all three tasks, which is what the default call site needs.

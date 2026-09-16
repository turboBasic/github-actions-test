# Scenario: custom mise task names

## What it exercises

That `project-ci.yml`'s four task names are fixed, by keeping this repository's own instead.

The tasks here are `check`, `types` and `spec`. The call site is otherwise `main`'s. Nothing is passed to
reconcile the two, because at `@v0.3` there is nothing to pass: the task names are the interface.

## Why it is worth a branch

This is the failure every consumer migrating off `python-ci` meets first, and the only one the capability
cannot soften. `lint-task`, `typecheck-task` and `test-task` existed at `@v0.2` for exactly this
repository shape; retiring them moved the obligation into the consumer's `mise.toml`, and a branch is the
only place to see what declining it costs.

It is also worth seeing *how* it fails. The run does not stop at an unknown input or a schema error —
either would be caught at the call, before a job exists. It gets as far as invoking the task runner,
which is what reports that the name does not exist.

## Expected result

`python / project-ci` **fails**, at the Lint stage, before Build, Typecheck or Test is reached.

The assertion is the log rather than the colour: `mise ERROR no task lint found`, followed by the
available tasks — `check`, `ci`, `deps`, `resync`, `setup`, `spec`, `types`. That list is the fix, printed
by the tool that knows it, which is why `project-ci` pre-flights nothing here.

## Observed at `@v0.1` and `@v0.2`

PR #12 green, with three steps running `[check] $ uv run ruff check .`, `[types] $ uv run pyright` and
`[spec] $ uv run pytest` — the override path, through the three `*-task` inputs. Both refs still resolve
and still carry them, so the green half of this scenario is pinned rather than lost.

## Do not merge, and do not rename

`main` uses the contract's names, which is what a consumer copies out of the README. Renaming the tasks
here turns this branch into `main`, and the scenario into nothing.

# Scenario: stages switched off for a repo that lacks the tasks

## What it exercises

`project-ci.yml`'s `run-typecheck: false` and `run-test: false`, in the situation they were added for.

This branch **deletes** the `typecheck` and `test` tasks from `mise.toml`. That is `opus-magnum`'s
actual shape — `docs/consumers.md` records that its `[tasks.*]` are all `make` wrappers, so it defines
neither task and needs both inputs.

`run-build: false` rides along, nothing here having a build target, which leaves `lint` as the only stage
on. One stage is the minimum: switch that off too and the call is refused, which
[test/stages-all-off](../scenario-stages-all-off/README.md) is the branch for.

## Why it is worth a branch

Passing `run-test: false` in a repo that *has* a test task proves only that the `if:` works. It says
nothing about the case the input exists for: a repo where leaving the default would fail. Deleting the
tasks is what makes the test real.

## Expected result

`python / project-ci` **passes**, having run checkout, the tool install and `mise run lint` — and nothing
else. The Build, Typecheck and Test steps report as skipped.

Flip either input back to its default on this branch and the run fails naming the task that does not
exist. That failure is the thing `opus-magnum` would hit without these inputs.

## Observed

At `@v0.1`, PR #13 green with step conclusions `Lint: success`, `Typecheck: skipped`, `Test: skipped`,
and `Install from the lockfile` still running — the inputs switched off the stages, not the preparation
the capability did on the component's behalf.

At `@v0.3` there is no such step to read: dependency installation is a `depends` of the `lint` task, so
it happens inside the one stage still on. A repository that switched every stage off would install
nothing at all, which is one reason that call is refused rather than run.

## Do not merge

`main` defines every task bar `build`, which is what its own call sites need.

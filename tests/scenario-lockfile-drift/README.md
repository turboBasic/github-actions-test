# Scenario: lockfile drift

## What it exercises

That dependency integrity survived moving out of the capability and into the consumer's own task.

This branch bumps `[project].version` to `0.9.0` and leaves `uv.lock` alone. `uv.lock` records the
project's own version, so `uv sync --locked` refuses — even though no dependency changed.

## Why it is worth a branch

At `@v0.2` this was a step inside `python-ci`, run before any stage and switchable by nothing. At `@v0.3`
the capability installs nothing on a component's behalf: `--locked` lives in this repository's `deps`
task, which every stage depends on. The check is the same; the owner is not.

That is the interesting half. A consumer could migrate, keep its four task names, and still lose this by
dropping `depends = ["deps"]` — and nothing would say so, the stages simply running against whatever was
resolvable. This branch is the proof the guard still fires where it now lives.

The surprising half is unchanged: a *version* bump counts as drift when no dependency moved. `--locked`
reads easily as being about dependency versions only.

## Expected result

`python / project-ci` **fails**, at the Lint stage rather than at a step of the capability's own, because
that is where `deps` runs first:

```text
error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.
hint: To update the lockfile, run `uv lock`.
[deps] ERROR task failed
```

`go / project-ci` stays **green** over the same tree: a different component, its own dependency graph, its
own `deps`. Two components, two verdicts — which is the reason each gets a check name of its own.

The fix is one command, `uv lock`, and the point is that CI says so rather than silently syncing to
something the lockfile does not describe.

## Observed at `@v0.1`

PR #15 red at *Install from the lockfile* — a step name that no longer exists — with `Lint`, `Typecheck`
and `Test` all skipped. The pull request reported `BLOCKED`, which is what makes this branch the control
for [test/checks-disabled](../scenario-checks-disabled/README.md): the ruleset is enforcing, so a skipped
check counting as passed there is a fact about skipping, not about a ruleset that was off.

A second check failed there too — `advisory / prek-advisory`, on its own `uv sync --locked` rather than on
a lint finding, a check named non-blocking failing. That was `TD-002` upstream and this run was its
evidence. Both went at `@v0.2`.

## Do not merge, and do not fix

This branch is meant to stay red. A green version of it would prove nothing. `0.9.0` is deliberately far
ahead of anything this repository will release soon, so a release landing on `main` cannot quietly erase
the drift — which is exactly what happened to the previous version of this scenario, whose `0.3.0` bump
`main` eventually reached.

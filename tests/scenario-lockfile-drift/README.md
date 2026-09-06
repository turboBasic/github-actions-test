# Scenario: lockfile drift

## What it exercises

`python-ci.yml`'s `uv sync --locked` step, in the failure the README warns about:

> Requires a `mise.toml` with the tasks being run, and a `uv.lock` — the workflow runs
> `uv sync --locked`, so any lockfile drift fails it, **including a project version bumped without
> re-running `uv lock`**.

This branch bumps `[project].version` from `0.1.0` to `0.2.0` and leaves `uv.lock` alone.

## Why it is worth a branch

That sentence in the README is a claim about behaviour, and the surprising half of it is the bracketed
part — that a *version* bump counts as drift, when no dependency changed. It is easy to read
`--locked` as being about dependency versions only.

`github-actions` hit this for real: cutting v2.0.2 required `uv lock` after `cz bump`, and skipping it
would have failed CI in every consumer at once. `CONTRIBUTING.md` says so because of this behaviour;
this branch is the behaviour.

## Expected result

`ci / python-ci` **fails**, at *Sync dependencies*, before any lint, typecheck or test runs. The
message names the lockfile as out of date.

The fix is one command — `uv lock` — and the point of the scenario is that CI says so rather than
silently syncing to something the lockfile does not describe.

## Observed at `@v4`

PR #15 red at *Sync dependencies*, with `Lint`, `Typecheck` and `Test` all skipped, on:

```text
error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.
hint: To update the lockfile, run `uv lock`.
```

The pull request reports `BLOCKED`, which is what makes this branch the control for
[test/checks-disabled](../scenario-checks-disabled/README.md): the ruleset is enforcing, so a skipped
check counting as passed there is a fact about skipped, not about a ruleset that was off.

`advisory / prek-advisory` fails here too, on its own `uv sync --locked` rather than on a lint finding
— the check named non-blocking, failing. That is `TD-1` in `turboBasic/github-actions`'
technical-debt register, and this run is the evidence it cites.

## Do not merge, and do not fix

This branch is meant to stay red. A green version of it would prove nothing.

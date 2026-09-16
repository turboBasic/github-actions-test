# Scenario: the lint task that never absorbed the hook runner

## What it exercises

The obligation a consumer inherits when the changed-files bypass is retired, by declining to meet it.
Identical to [test/lint-task-absorbs-prek](../scenario-lint-task-absorbs-prek/README.md) in every
respect but one: this branch **reverts** `mise.toml`'s `lint` task to `uv run ruff check .`, against a
`main` that calls the hook runner.

That revert is the scenario. `main` meets the obligation, so declining it takes an edit rather than an
omission — and the edit is a two-line one that reads as housekeeping, which is the reason this branch
exists.

`@v0.1` still carries the bypass and the advisory capability it compensated for, so this scenario says
nothing about that ref.

## Why it is worth a branch

Because the coverage this loses is invisible from the check summary, and a green check is the one
nobody investigates.

`project-ci.yml` owns no linter — it runs the task it is given. At `@v0.1` that was survivable:
`variants / python-ci` ran prek over the diff and `advisory / prek-advisory` ran it over the whole tree,
so `.pre-commit-config.yaml`'s whitespace hooks reached CI even though the lint task ignored them. Both
routes are long gone, and a lint task that does not call prek means nothing in CI does.

The upstream README states the obligation in prose. This branch is the demonstration: the same
violation its twin blocks on passes here, unremarked, on a required check.

## Expected result

| Check | Expected | Why |
| --- | --- | --- |
| `python / project-ci` | 💚 | `mise run lint` is ruff, and ruff does not look for trailing whitespace |
| `python-no-typecheck / project-ci` | 💚 | same task, same blindness |
| `go / project-ci` | 💚 | a different component, with a lint task of its own that this branch does not touch |

**Green is the finding.** The tree carries a violation that `prek run --all-files` fails on — the same
file, byte for byte, that reddens the twin — and every check here passes. Nothing in the run mentions
it. That is not a fault in the scenario; it is the whole scenario.

The assertion in the log is the absence: the lint step shows `uv run ruff check .` and `All checks
passed`, with no hook runner invoked anywhere in the job.

## The whole diff against `main`

- `mise.toml`'s `lint` task, reverted to `uv run ruff check .`. That is the deviation under test.
- This README and the broken file.

Nothing else. The ref pin and the call sites come from `main`, and keeping local copies would conflict
with every future rebase for no gain.

## Do not merge, and do not fix

Neither the broken file nor the lint task. Fixing either turns this into its twin, and the pair only
says anything together. `mise run setup` installs prek's git hooks, after which a plain `git commit`
here strips the whitespace — commit with `--no-verify` or check `git diff` first.

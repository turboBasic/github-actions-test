# Scenario: the lint task absorbs the hook runner

## What it exercises

`python-ci.yml`'s lint stage once the changed-files bypass is gone: it delegates to `mise run lint`
unconditionally, so what the published check judges is exactly what that task judges.

**This branch changes nothing but the tree it is judged over.** It takes `main`'s `@v0.2` call sites and
`main`'s lint task — `prek run --all-files --show-diff-on-failure` — and adds one trailing-whitespace
violation. That is the whole diff, which is the point: `main` is already the arrangement under test, and
the branch only supplies something for it to find.

`@v0.1` still carries the bypass and the advisory capability it compensated for, so this scenario says
nothing about that ref.

## Why it is worth a branch

Because this is the arrangement that closes the gap `prek-advisory` existed to paper over, and the
verdict is only interesting next to its twin.

At `@v0.1` a trailing-whitespace violation in this repository reached CI two ways, neither of them the
required check: `variants / python-ci` ran prek over the pull request's own diff, and
`advisory / prek-advisory` ran it over the whole tree and reported in a comment while staying green.
`mise run lint` was `uv run ruff check .`, and ruff does not look for trailing whitespace, so the
required check never saw it.

At this ref both of those routes are gone. The finding either reaches the required check through the
lint task or it reaches nothing at all — which is what
[test/lint-task-without-prek](../scenario-lint-task-without-prek/README.md) is the other half of. Same
violation, same ref, the lint task the only difference, opposite verdicts.

## Expected result

| Check | Expected | Why |
| --- | --- | --- |
| `ci / python-ci` | ❤️ | `mise run lint` is the hook runner now, and `trailing-whitespace` finds the planted line |
| `variants / python-ci` | ❤️ | same task, same finding; `run-typecheck: false` is all that still distinguishes this job |

The assertion is in the log, not the colour: the lint step must show `trim trailing whitespace ...
Failed` naming this file, and `--show-diff-on-failure` must print the one-line diff that fixes it. A
red check whose log says `uv run ruff check` instead means the absorb did not land.

`ci / python-ci` is a required context here, so this pull request is not mergeable — deliberately, the
same way `test/lockfile-drift` is not.

## Why the diff is only the broken file

It was larger when this branch was opened against the unreleased upstream branch: it carried the ref
pin, the `mise.toml` absorb, and the deletion of the `prek-advisory.yml` call site. `main` took all
three when it repinned to `@v0.2`, so keeping local copies would leave a scenario that conflicts with
every future rebase for no gain. A scenario branch differing from `main` only in what it exercises is
the shape `rebase-scenarios.yml` can replay without a human.

## Do not merge, and do not fix

The file is meant to stay broken. `mise run setup` installs prek's git hooks, and after that a plain
`git commit` here strips the whitespace for you — as does any local `mise run lint`, which is now the
same thing. Check `git diff` before committing rather than trusting the exit code.

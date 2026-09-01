# github-actions-test

Test consumer for [`turboBasic/github-actions`][upstream]. It exists to run those workflows the way a
real repository runs them, at the `@v2` tag consumers actually pin.

Every linter upstream passes on a workflow that no caller can run, so lint there proves nothing about
whether a call site works. This repository is the caller.

| Call site | What it exercises |
| --- | --- |
| `.github/workflows/ci.yml` | `python-ci.yml@v2` twice: once at every default, once with `lint-changed-only`, `hook-stage: pre-push` and `run-typecheck: false` |
| `.github/workflows/commit-messages.yml` | `conventional-commits.yml@v2` — PR title and every commit in the range |
| `.github/workflows/precommit-advisory.yml` | `precommit-advisory.yml@v2` — the whole tree, non-blocking, as one updated PR comment |
| `.github/workflows/pr-description.yml` | `actions/populate-pr-description@v2` — renders `.github/PULL_REQUEST_TEMPLATE.md` from the commit range |

## Scenario branches

Each branch under `test/scenario-*` exercises one input combination and documents it in
`tests/scenario-<name>/README.md`. They are not for merging: several change `mise.toml` or a workflow
in ways `main` must not adopt, and one is meant to stay red.

| Branch | Exercises | Ends |
| --- | --- | --- |
| `test/scenario-custom-task-names` | `lint-task`, `typecheck-task`, `test-task` against renamed mise tasks | green |
| `test/scenario-stages-off` | `run-typecheck: false`, `run-tests: false` with those tasks **deleted** — `opus-magnum`'s shape | green |
| `test/scenario-mise-version-pin` | `mise-version` forwarded to `jdx/mise-action` | green |
| `test/scenario-lockfile-drift` | `uv sync --locked` against a version bump with no `uv lock` | **red, on purpose** |
| `test/scenario-checks-disabled` | `check-title: false`, `check-commits: false` — and what a skipped required check does | green, having checked nothing |

A green branch proves nothing on its own, so each README names the assertion in the log rather than
the colour: which `TASK` the step received, which mise version installed, which step failed first.

## Required checks

`main` carries a ruleset requiring `ci / CI`, `commits / PR title` and `commits / Commit messages` —
the same three contexts as upstream, so the check-name composition (`<caller job> / <called job>`) is
under test too.

`variants / CI` is deliberately **not** required. The scenario branches replace `ci.yml` with a single
job, so that context never reports there, and a required context that no job reports blocks the pull
request forever. That is the trap `tests/test_action_pins.py` guards upstream, met here by leaving the
context optional.

The Python here has no purpose beyond giving `python-ci.yml` something to lint, typecheck and test.
`src/probe` is one function and `tests/` asserts it.

`.pre-commit-config.yaml` carries a `pre-push` hook deliberately: without one, `hook-stage: pre-push`
would look wired up while running nothing.

## Local

```sh
mise run setup
mise run ci
```

<!-- Links -->

[upstream]: https://github.com/turboBasic/github-actions

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

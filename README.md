# github-actions-test

Test consumer for [`turboBasic/github-actions`][upstream]. It exists to run those workflows the way a
real repository runs them, at the `@v4` tag consumers actually pin.

Every linter upstream passes on a workflow that no caller can run, so lint there proves nothing about
whether a call site works. This repository is the caller.

| Call site | What it exercises |
| --- | --- |
| `.github/workflows/ci.yml` | `python-ci.yml@v4` twice: once at every default, once with `lint-changed-only`, `hook-stage: pre-push`, `run-typecheck: false` and `cache-prek` |
| `.github/workflows/commit-messages.yml` | `conventional-commits.yml@v4` — PR title and every commit in the range |
| `.github/workflows/prek-advisory.yml` | `prek-advisory.yml@v4` — the whole tree, non-blocking, as one updated PR comment |
| `.github/workflows/pr-description.yml` | `actions/populate-pr-description@v4` — renders `.github/PULL_REQUEST_TEMPLATE.md` from the commit range |

## Scenario branches

Each branch under `test/*` pins one caller-side input combination — the shapes nothing inside
`github-actions` can exercise itself, because its own self-calls take the defaults. **The branches are
the artifacts; this table is the index.** A scenario lives on its branch and documents itself in a
README the table links, mirrored onto `main` so the set reads without checking out five branches, and
so a scenario cannot be quietly lost by deleting a branch nobody remembered.

None of them is for merging: several change `mise.toml` or a workflow in ways `main` must not adopt,
and one is meant to stay red. Each still carries an open pull request, because most of these workflows
only run from one.

| Branch | Exercises | Ends |
| --- | --- | --- |
| [test/custom-task-names](tests/scenario-custom-task-names/README.md)<br>[PR #12](https://github.com/turboBasic/github-actions-test/pull/12) | `python-ci.yml`'s `lint-task`, `typecheck-task` and `test-task`, with this repo's mise tasks renamed to `check`, `types` and `spec` | 💚 The override path is never taken upstream, since `github-actions` self-calls with the defaults. Rename a task without wiring the input and the job fails with `task not found`. |
| [test/stages-off](tests/scenario-stages-off/README.md)<br>[PR #13](https://github.com/turboBasic/github-actions-test/pull/13) | `python-ci.yml`'s `run-typecheck: false` and `run-tests: false`, with those tasks **deleted** from `mise.toml` | 💚 Runs only checkout, `uv sync --locked` and `mise run lint`. Deleting the tasks is what makes it real — passing the inputs in a repo that *has* them proves only that the `if:` works. This is `opus-magnum`'s actual shape. |
| [test/mise-version-pin](tests/scenario-mise-version-pin/README.md)<br>[PR #14](https://github.com/turboBasic/github-actions-test/pull/14) | `python-ci.yml`'s `mise-version`, pinned to `2026.9.0` and forwarded to `jdx/mise-action` | 💚 but **the log line is the assertion**: the mise-action step must report `2026.9.0` rather than the newest release. A green job alone cannot tell a forwarded input from an ignored one. `opus-magnum` is the only real consumer that pins it. |
| [test/lockfile-drift](tests/scenario-lockfile-drift/README.md)<br>[PR #15](https://github.com/turboBasic/github-actions-test/pull/15) | `python-ci.yml`'s `uv sync --locked`, with `[project].version` bumped to `0.2.0` and `uv.lock` left alone | ❤️ **On purpose**, at *Sync dependencies*, before any lint or test runs. The surprising half is that a *version* bump counts as drift when no dependency changed. `github-actions` hit this cutting v2.0.2. Do not fix. |
| [test/checks-disabled](tests/scenario-checks-disabled/README.md)<br>[PR #16](https://github.com/turboBasic/github-actions-test/pull/16) | `conventional-commits.yml`'s `check-title: false` and `check-commits: false` | 💚 **having checked nothing** — the most dangerous behaviour in the set. Both checks report *success without running*, because GitHub counts a skipped job as passed, and a skipped **required** check satisfies the ruleset, so the branch is `MERGEABLE` with two gates that validated nothing. Drop a check and remove its required context in the same change. |
| [test/advisory-comment](tests/scenario-advisory-comment/README.md)<br>[PR #24](https://github.com/turboBasic/github-actions-test/pull/24) | `prek-advisory.yml` past its `if: steps.prek.outputs.failed == 'true'` gate — the warning, the summary and the find-or-update PR comment — via one trailing-whitespace violation in Markdown | 💚 **while reporting a lint failure**, the only check in the set where green means the opposite of a passing lint. The pull request still ends ❤️, because `variants / python-ci` fails on the same violation — which is what its title carries. The other five reach this code in neither direction: four pass prek, and `test/lockfile-drift` dies two steps earlier with the action `skipped`. Two pushes, one comment: same id, moved `updated_at`. |

A green branch proves nothing on its own, so each README names the assertion in the log rather than
the colour: which `TASK` the step received, which mise version installed, which step failed first.

The **Ends** column above is the colour of the behaviour under test; each pull request title carries
the same pair for the colour of its own check summary — 💚 where every check is expected to pass, ❤️
where one is expected to fail by design. They differ only on `test/advisory-comment`.

## Required checks

`main` carries a ruleset requiring `ci / python-ci`, `commits / pr-title` and
`commits / commit-messages` — the same three contexts as upstream, so the check-name composition
(`<caller job> / <called job>`) is under test too. `v4` renamed the called half of all three, and this
repository's ruleset moved with the repin: leaving the old contexts required would block every pull
request on a check nothing reports.

`variants / python-ci` is deliberately **not** required. A scenario whose input combination lives in
`ci.yml` replaces that file with a single job — `test/custom-task-names`, `test/mise-version-pin` and
`test/stages-off` all do — so the context never reports there, and a required context that no job
reports blocks the pull request forever. That is the trap `tests/test_action_pins.py` guards upstream,
met here by leaving the context optional. The three scenarios that configure something else keep this
file as `main` has it, so `variants / python-ci` does report on theirs — and on
`test/advisory-comment` it reports **red**, which is the point of that branch rather than a fault in
it. Leaving the context optional is what keeps that pull request mergeable-in-principle while it
carries a deliberate lint failure.

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

## Versioning here

This repository is deliberately at `0.x`, so it exercises the 0.x compatibility line
in `release.yml`: the moving ref is `v0.1` rather than `v0`, a breaking change may ship
as `0.2.0`, and no `v0` is ever published. See turboBasic/github-actions#107.

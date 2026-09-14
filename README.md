# github-actions-test

Test consumer for [`turboBasic/github-actions`][upstream]. It exists to run those workflows the way a
real repository runs them, at `@v0.2`, the ref consumers actually pin.

Every linter upstream passes on a workflow that no caller can run, so lint there proves nothing about
whether a call site works. This repository is the caller.

| Call site | What it exercises |
| --- | --- |
| `.github/workflows/ci.yml` | `python-ci.yml@v0.2` twice: once at every default, once with `run-typecheck: false` |
| `.github/workflows/release-on-merge.yml` | `release.yml@v0.2` gated on a second `python-ci.yml@v0.2` call, plus the `workflow_dispatch` and `dry-run` path, and — ordered behind `release`, never beside it — `release-proposal.yml@v0.2`: works out the next version from the range and opens the pull request whose merge this workflow then releases, with the App credentials passed as declared secrets |
| `.github/workflows/commit-messages.yml` | `conventional-commits.yml@v0.2` — PR title and every commit in the range |
| `.github/workflows/dependency-guard.yml` | `dependency-review.yml@v0.2` at the default severity floor — the only call to it from outside `github-actions` |

Two call sites went with the repin, their capabilities having been retired upstream rather than
changed: `prek-advisory.yml`, whose whole-tree advisory comment `@v0.2` replaces with a lint task that
covers the tree in the blocking check, and `pr-description.yml`, retired a release earlier. `@v0.1`
still resolves and still has both.

`mise.toml`'s `lint` task calls the hook runner rather than ruff directly, and that is not incidental:
`python-ci` runs the task it is given and owns no linter, so at `@v0.2` a task calling only ruff would
leave `.pre-commit-config.yaml`'s whitespace hooks checked by nothing in CI.
[test/lint-task-without-prek](tests/scenario-lint-task-without-prek/README.md) is the branch that shows
what that looks like.

## Scenario branches

Each branch under `test/*` pins one caller-side input combination — the shapes nothing inside
`github-actions` can exercise itself, because its own self-calls take the defaults. **The branches are
the artifacts; this table is the index.** A scenario lives on its branch and documents itself in a
README the table links, mirrored onto `main` so the set reads without checking out every branch, and
so a scenario cannot be quietly lost by deleting a branch nobody remembered.

None of them is for merging: several change `mise.toml` or a workflow in ways `main` must not adopt,
and one is meant to stay red. Each still carries an open pull request, because most of these workflows
only run from one.

`.github/workflows/rebase-scenarios.yml` replays every one of them onto `main` after each merge, so a
scenario is always testing `@v0.2` against the base `main` actually has. A conflict aborts and fails that
run rather than being resolved — which side a scenario meant is not a runner's call. The two branches
that pin the ref in a file of their own rather than inheriting `main`'s are the ones a repin can conflict
with; the rest take `ci.yml` as `main` has it and follow the ref automatically.

A branch whose rebase carries a change to a workflow file is a different failure: the rebase succeeds,
and only the push is refused, for a token permission rather than a conflict. The run reports that case as
a refused push naming the branch, not a conflict, and the App token requests `workflows` write alongside
`contents` write so the push that started this — repinning every call site under `.github/workflows/` —
goes through.

It force-pushes under the `turbobasic-release-proposal` App, not `GITHUB_TOKEN`, because an event caused
by `GITHUB_TOKEN` starts no workflow run: the same push made with it would move all six pull requests
onto a new base and re-run none of their checks. `RELEASE_APP_CLIENT_ID` and `RELEASE_APP_PRIVATE_KEY`
are set here as repository secrets, the same pair `github-actions` holds, and this is one of the App's
two uses here — `release-on-merge.yml`'s `proposal` job passes the same credentials to
`release-proposal.yml` as declared secrets. The installation is `repository_selection: selected`, so
adding this repository to its list is a
prerequisite the secrets alone do not cover.

| Branch | Exercises | Ends |
| --- | --- | --- |
| [test/custom-task-names](tests/scenario-custom-task-names/README.md)<br>[PR #12](https://github.com/turboBasic/github-actions-test/pull/12) | `python-ci.yml`'s `lint-task`, `typecheck-task` and `test-task`, with this repo's mise tasks renamed to `check`, `types` and `spec` | 💚 The override path is never taken upstream, since `github-actions` self-calls with the defaults. Rename a task without wiring the input and the job fails with `task not found`. |
| [test/stages-off](tests/scenario-stages-off/README.md)<br>[PR #13](https://github.com/turboBasic/github-actions-test/pull/13) | `python-ci.yml`'s `run-typecheck: false` and `run-tests: false`, with those tasks **deleted** from `mise.toml` | 💚 Runs only checkout, `uv sync --locked` and `mise run lint`. Deleting the tasks is what makes it real — passing the inputs in a repo that *has* them proves only that the `if:` works. This is `opus-magnum`'s actual shape. |
| [test/lockfile-drift](tests/scenario-lockfile-drift/README.md)<br>[PR #15](https://github.com/turboBasic/github-actions-test/pull/15) | `python-ci.yml`'s `uv sync --locked`, with `[project].version` bumped to `0.3.0` and `uv.lock` left alone | ❤️ **On purpose**, at *Install from the lockfile*, before any lint or test runs. The surprising half is that a *version* bump counts as drift when no dependency changed. `github-actions` hit this cutting v2.0.2. Do not fix. |
| [test/checks-disabled](tests/scenario-checks-disabled/README.md)<br>[PR #16](https://github.com/turboBasic/github-actions-test/pull/16) | `conventional-commits.yml`'s `check-title: false` and `check-commits: false` | 💚 **having checked nothing** — the most dangerous behaviour in the set. Both checks report *success without running*, because GitHub counts a skipped job as passed, and a skipped **required** check satisfies the ruleset, so the branch is `MERGEABLE` with two gates that validated nothing. Drop a check and remove its required context in the same change. |
| [test/lint-task-absorbs-prek](tests/scenario-lint-task-absorbs-prek/README.md)<br>[PR #57](https://github.com/turboBasic/github-actions-test/pull/57) | `python-ci.yml`'s lint stage once the changed-files bypass is retired: it delegates to `mise run lint` unconditionally, and here that task is `prek run --all-files --show-diff-on-failure` over one planted trailing-whitespace violation | ❤️ **On purpose.** The finding reddens the required check, which at `@v0.1` it could not: the lint task was ruff, and the two routes that did carry it — `lint-changed-only` and `advisory / prek-advisory` — were the diff and an advisory comment. The log is the assertion: `trim trailing whitespace…Failed` naming the file, with the diff that fixes it. |
| [test/lint-task-without-prek](tests/scenario-lint-task-without-prek/README.md)<br>[PR #58](https://github.com/turboBasic/github-actions-test/pull/58) | the same ref, the same violation byte for byte, and `mise.toml`'s lint task left as `uv run ruff check .` — the obligation `@v0.2` hands a consumer, declined | 💚 **and green is the finding.** Every check passes over a tree the hook runner fails on, and nothing in the run mentions it. `python-ci` owns no linter, so a lint task that does not call prek means nothing in CI does. The assertion is an absence: `uv run ruff check .`, `All checks passed`, and no hook runner anywhere in the job. |
| [test/release-proposal](tests/scenario-release-proposal/README.md)<br>[PR #54](https://github.com/turboBasic/github-actions-test/pull/54) | `release-proposal.yml`'s declared secrets, by withholding `app-private-key` from a second call site. The passing half needs no branch — `release-on-merge.yml`'s `proposal` job on `main` runs it on every merge | ❤️ `startup_failure` **with no job at all**, the assertion being the emptiness rather than the colour. GitHub refuses a caller that omits a required secret before the workflow runs, so nothing logs, nothing annotates, and no context is composed. It is the whole argument for declaring the secrets instead of `secrets: inherit`, where a missing one would surface later as an empty key. |

A green branch proves nothing on its own, so each README names the assertion in the log rather than
the colour: which `TASK` the step received, which mise version installed, which step failed first.

The **Ends** column above is the colour of the behaviour under test; each pull request title carries
the same pair for the colour of its own check summary — 💚 where every check is expected to pass, ❤️
where one is expected to fail by design. They differ on two: `test/lint-task-without-prek`, where a
green summary is itself the finding, and `test/release-proposal`, whose failure composes no check at all
and so cannot show in a summary.

## Required checks

`main` carries a ruleset requiring `ci / python-ci`, `commits / pr-title` and
`commits / commit-messages` — the same three contexts as upstream, so the check-name composition
(`<caller job> / <called job>`) is under test too. The called half has been renamed twice now, and this
repository's ruleset moved with it both times: leaving a retired context required blocks every pull
request on a check nothing reports, and the only symptom is a check that never appears.
`PopulationCircles2026` met exactly that on the `@v0.1` repin.

`variants / python-ci` is deliberately **not** required. A scenario whose input combination lives in
`ci.yml` replaces that file with a single job — `test/custom-task-names` and `test/stages-off` both
do — so the context never reports there, and a required context that no job
reports blocks the pull request forever. That is the trap `tests/test_action_pins.py` guards upstream,
met here by leaving the context optional. The scenarios that configure something else keep this
file as `main` has it, so `variants / python-ci` does report on theirs — and on
`test/lint-task-absorbs-prek` it reports **red**, which is the point of that branch rather than a fault
in it. Leaving the context optional is what keeps that pull request mergeable-in-principle while it
carries a deliberate lint failure. `ci / python-ci` is required and red there, so it is not mergeable in
fact, which is the same footing `test/lockfile-drift` stands on.

`test/release-proposal` is the one scenario whose failure composes **no context whatsoever**. A run
refused for a missing secret never reaches a job, so it produces no check run to require, to skip or to
read — which is why that branch's evidence is its README and its Actions tab rather than its check
summary.

The Python here has no purpose beyond giving `python-ci.yml` something to lint, typecheck and test.
`src/probe` is one function and `tests/` asserts it.

`.pre-commit-config.yaml` is what `mise run lint` runs, so it is what `python-ci`'s lint stage judges.
Its `pre-push` hook is outside that — a plain `prek run` fires the pre-commit stage — and exists now as a
local guard rather than as something for a retired `hook-stage` input to reach.

## Local

```sh
mise run setup
mise run ci
mise run resync
```

`resync` is the local half of `rebase-scenarios.yml`: because that workflow force-pushes, a local
`test/*` branch is stale as soon as anything lands on `main`, and `git pull` on one would replay the
discarded tip as a merge. The task switches to `main`, pulls, prunes, refetches tags, then hard-resets
every local `test/*` ref to its origin counterpart — **discarding local commits on those branches**,
which is the only correct treatment of a ref the remote rewrites.

It then deletes any local branch whose upstream is `[gone]`, which is what a squash merge with
`--delete-branch` leaves behind. `[gone]` is the whole guard: a branch that was never pushed has no
upstream, so it is never a candidate, and the deletion needs `-D` only because a squashed commit
appears in no ancestry `-d` can see.

<!-- Links -->

[upstream]: https://github.com/turboBasic/github-actions

## Versioning here

This repository is deliberately at `0.x`, so it exercises the 0.x compatibility line
in `release.yml`: the moving ref is `v0.1` rather than `v0`, a breaking change may ship
as `0.2.0`, and no `v0` is ever published. The rule is
[ADR 0002](https://github.com/turboBasic/github-actions/blob/main/docs/decisions/0002-start-the-line-at-0-1-0.md)
and the pinning table in that repository's README.

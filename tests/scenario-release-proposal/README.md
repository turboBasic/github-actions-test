# Scenario: the release proposal

## What it exercises

`release-proposal.yml` reached the way a consumer reaches it — by `workflow_call`, across a dependency
edge, with the App credentials arriving as declared secrets rather than as two fixed `secrets.RELEASE_APP_*`
names read inside the capability.

Two call sites on one push, so both outcomes land in one run pair:

| Workflow | Passes | Exercises |
| --- | --- | --- |
| `propose-on-merge.yml` | both secrets | the whole path: range, version, branch write, pull request |
| `propose-no-secrets.yml` | `app-client-id` only | the refusal when a required secret is withheld |

## Why it is worth a branch

Because the upstream repository cannot reach this at all. Its own `propose-on-merge.yml` resolves the
capability by path, which exercises the workflow's *body* but not its *entry point* — a `workflow_call`
signature only has to be right when something calls it from outside, and by then the secrets are a
consumer's to name.

The second workflow is the half that cannot be tested upstream in any form. A withheld secret is refused
by GitHub before the workflow runs, so nothing in a test suite and no assertion about the YAML can
demonstrate it. The only way to see it is to withhold one.

## Expected result

| Run | Expected | Why |
| --- | --- | --- |
| `propose-on-merge` | 💚 and a pull request | the range since `v0.2.0` renders notes, so a version is proposed |
| `propose-no-secrets` | ❤️ `startup_failure`, no jobs | a required secret a caller does not pass refuses the run before any job exists |

## Observed at `@feat/publish-release-proposal-as-a-callable-capability`

Both as expected, first push, no retries.

**`propose-on-merge` → success.** It opened [#53][pr] — `chore: release v0.2.1`, from `release/next` into
this branch. Three things worth reading off it:

- **The diff is `pyproject.toml` and `uv.lock`, one line each.** Nothing else, and the two moved in one
  commit rather than two.
- **The body carries the real notes**, rendered with this repository's own `.cliff.toml` — the emoji
  section headings are ours, not a default. The capability invokes `git-cliff --config cliff.toml` and
  this repository's config is dot-prefixed; git-cliff resolves the dotted name itself, so the
  consumer's grouping is what renders.
- **The commit carries the trailer**, `Computed-Version: 0.2.1`, which is what a later refresh compares
  against to tell a person's edit from a fresh computation.

`0.2.1` and not `0.3.0` is correct, and it is the thing most likely to be misread here. The range
contains `feat: call dependency-review as a consumer does (#49)`, but below `1.0.0` the *minor* is the
break axis — so a feature is a patch, and only a break moves the minor.

**`propose-no-secrets` → `startup_failure`, and nothing else at all.** The refusal is complete:

```text
gh api .../actions/runs/34836304807/jobs --jq .total_count   → 0
gh run view 34836304807 --log                               → failed to get run log: log not found
gh api .../check-suites/<id>/check-runs                      → (empty)
```

No job, no log, no check run, no annotation. The exact wording is legible in the browser and nowhere
else, which makes this the same failure mode as an ungranted permission — and the reason the capability
declares its secrets rather than taking `secrets: inherit`, where a missing one would instead surface
much later as the App-token step holding an empty key.

The context the passing run composed is `proposal / propose`, matching what the upstream README claims.

## When this branch changes

Both workflows carry a branch-scoped `push:` trigger and a feature-branch ref. Once the capability is
released, they become `push: branches: [main]` at the released ref — at which point `propose-no-secrets.yml`
should be deleted rather than repointed. It exists to fail, and a scenario branch is where a failing call
site belongs, not `main`.

[pr]: https://github.com/turboBasic/github-actions-test/pull/53

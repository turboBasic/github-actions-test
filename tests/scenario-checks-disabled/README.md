# Scenario: both conventional-commits checks disabled

## What it exercises

`conventional-commits.yml`'s `check-title: false` and `check-commits: false`, and the trap the README
attaches to them:

> The same holds for `check-title: false` and `check-commits: false`, which gate the same conditions:
> drop a check and remove its context from your required status checks in the same change, or the
> branch protection page keeps showing a gate that is no longer there.

Both jobs carry `if: inputs.check-* && github.event_name == 'pull_request'`. Setting the input to
`false` skips the job, and **GitHub reports a skipped job as success**.

## Why it is worth a branch

This is the most dangerous behaviour in the whole set, because it is invisible in exactly the place
someone would look. The check name still appears on the PR. It is still green. A required status check
named `commits / PR title` still reports. Nothing anywhere says "this validated nothing".

`github-actions` itself relies on the same mechanism for a different reason — it is why
`conventional-commits.yml` must be called from `pull_request` and never `pull_request_target`, and why
`tests/test_action_pins.py` guards the check names. The failure mode is one input away.

## Expected result

`commits / PR title` and `commits / Commit messages` both **report success without running**. Open
either job and its steps are skipped.

Prove it by putting a non-conventional title on this PR: on `main`'s configuration the title check
fails, and here it stays green.

## Observed, against a ruleset

`commits / PR title` and `commits / Commit messages` are **required status checks** on this repo's
`main` ruleset. With both inputs `false` their conclusion is `skipped`, and GitHub reports this pull
request as `mergeStateStatus=CLEAN, mergeable=MERGEABLE`.

So a skipped required check *satisfies* branch protection. This is mergeable with two required gates
that validated nothing.

The control: `test/scenario-lockfile-drift`, whose `ci / CI` genuinely fails, reports `BLOCKED`. The
ruleset is enforcing; skipped just counts as passed.

## Do not merge

`main` keeps both checks on. This branch is a demonstration of what switching them off looks like from
outside — which is: exactly like passing.

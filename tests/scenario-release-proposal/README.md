# Scenario: the release proposal

## What it exercises

`release-proposal.yml@v0.1` reached across a dependency edge with a **required secret withheld**.

The passing half of this capability needs no branch: `.github/workflows/release-on-merge.yml`'s
`proposal` job on `main` runs it on every merge, so the proposal path is under test continuously. This
branch adds the one thing
`main` must not carry — a second call site passing `app-client-id` and nothing else.

## Why it is worth a branch

Because a withheld secret is refused by GitHub *before the workflow runs*. No assertion over the YAML
upstream can reach it, no job exists to log anything, and the capability's own code never executes. The
only way to see the behaviour is to withhold one from a real caller.

It matters because it is the whole argument for `release-proposal` declaring its secrets rather than
taking `secrets: inherit`. Under `inherit` a missing credential surfaces much later, as the App token
step holding an empty key, by which point the run has checked the tree out and looks like it is working.

## Expected result

| Run | Expected | Why |
| --- | --- | --- |
| `propose-no-secrets` | ❤️ `startup_failure`, **and no job at all** | a required secret a caller does not pass refuses the run before any job exists |

The assertion is the *emptiness*, not the colour. A run that reached a job — even a failing one — would
mean the secret was accepted as absent.

## Observed

At the capability's merge commit before release, and unchanged at `@v0.1`:

```text
gh api .../actions/runs/34836304807/jobs --jq .total_count   → 0
gh run view 34836304807 --log                               → failed to get run log: log not found
gh api .../check-suites/<id>/check-runs                      → (empty)
```

No job, no log, no check run, no annotation. GitHub's wording — `Secret app-private-key is required, but
not provided while calling.` — is legible in the browser and nowhere else, which is what makes this the
same class of failure as a permission a caller does not grant.

**It composes no context**, so it cannot appear as a check on this pull request and could never be
required in a ruleset. The pull request is green; the failure lives in the Actions tab. That is why this
README is the artifact rather than the check summary.

## What the passing half looked like

Recorded here because `main`'s call site is the thing under test and a run of it is worth one reading.
Observed on the pre-release ref, opening a proposal from a three-commit range:

- Title `chore: release v0.2.1`, head `release/next`.
- Diff exactly `pyproject.toml` and `uv.lock`, one line each, in **one** commit — a lockfile left behind
  would fail `uv sync --locked` on the very pull request whose merge is meant to release.
- Body carrying notes rendered from this repository's own `.cliff.toml`. The capability invokes
  `git-cliff --config cliff.toml` and this repository's config is dot-prefixed; git-cliff resolves the
  dotted name itself, so the consumer's own grouping is what renders.
- Commit carrying `Computed-Version: 0.2.1`, the trailer a later refresh compares against to tell a
  hand-edited version from a freshly computed one.
- Three pushes refreshed the one pull request rather than opening a second.

`0.2.1` and not `0.3.0` is correct, and is the most misreadable thing here: the range carried a `feat:`,
but below `1.0.0` the **minor** is the break axis, so a feature is a patch and only a break moves the
minor.

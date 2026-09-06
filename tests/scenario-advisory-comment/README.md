# Scenario: the advisory comment

## What it exercises

Everything in `actions/prek-advisory-pr` downstream of

```yaml
if: steps.prek.outputs.failed == 'true'
```

— the `::warning`, the `$GITHUB_STEP_SUMMARY` block, and the `actions/github-script` step that finds
its own previous comment by the `<!-- precommit-all-files-advisory -->` marker and updates it rather
than posting a second one.

The branch adds one Markdown file with a trailing-whitespace violation. That is the smallest breakage
that fails prek while leaving `uv sync --locked` and `mise run lint` alone.

## Why it is worth a branch

Because until this branch existed, that half of `prek-advisory.yml` had never run at `@v4`. The other
scenarios reach it in neither direction:

- Four of them **pass** prek, so `failed` is `'false'` and all three steps no-op.
- [test/lockfile-drift](../scenario-lockfile-drift/README.md) fails at *Sync dependencies*, two steps
  earlier, with the composite action reported as `skipped`. It never runs.

So a green `advisory / prek-advisory` everywhere else meant *prek ran*, never *the comment works*. The
one advisory comment that existed anywhere in this repository was posted on 2026-09-01 by a run still
called **Pre-commit advisory** — before the `v3` rename, five days before the `@v4` repin. Bump
`actions/github-script`, change which token the action is handed, or typo the marker, and nothing
would have said so.

Choosing *trailing whitespace in Markdown* is the load-bearing part. `mise run lint` is
`uv run ruff check .`, and ruff does not look for it, so the blocking check stays green and the
advisory comment is the only report of the finding. That is the arrangement the upstream README claims
`prek-advisory.yml` exists to provide.

## Expected result

| Check | Expected | Why |
| --- | --- | --- |
| `ci / python-ci` | 🟢 | `mise run lint` is ruff, which ignores trailing whitespace |
| `variants / python-ci` | 🔴 | `lint-changed-only` runs prek over the diff, and the broken file is in it |
| `advisory / prek-advisory` | 🟢 **while reporting the failure** | the prek step's exit code is swallowed by `set +e`, so the job succeeds and comments |

The third row is the assertion, and the colour is the wrong thing to read it by: this scenario is the
one where a green check means the opposite of a passing lint.

`variants` going red is not a flaw in the scenario. A single pull request cannot break a file outside
its own diff, so the changed-files run necessarily sees what the all-files run sees. What the branch
demonstrates is therefore the *pair* of verdicts on one finding — blocking in the changed-files run,
advisory in the all-files run — rather than a finding only the advisory could have caught.

## Observed at `@v4`

PR #24, two pushes, both with `advisory / prek-advisory` green and `Run prek on all files` failing
inside it.

```text
trim trailing whitespace.................................................Failed
- hook id: trailing-whitespace
- files were modified by this hook
  Fixing tests/scenario-advisory-comment/trailing-whitespace.md
```

The comment is one comment, and stayed one across both pushes:

| | First push | Second push |
| --- | --- | --- |
| comment id | `5559031460` | `5559031460` — unchanged |
| `created_at` | `11:53:15Z` | `11:53:15Z` — unchanged |
| `updated_at` | `11:53:15Z` | `11:54:16Z` — moved |
| `Details:` run | `34031497877` | `34031546003` — repointed |

Same id with a moved `updated_at` is the find-or-update branch; a second id would have been the
create branch firing twice. `created_at` staying put is what rules out delete-and-recreate.

## Two things this scenario ran into, which the branch is also the record of

**`--all-files` means all *tracked* files.** The first local pre-flight passed with the broken file
sitting untracked in the working tree, because prek asks git for the file list. A scenario built this
way is silently empty until the file is `git add`-ed.

**`trailing-whitespace` is a fixing hook.** Running `prek run` locally repairs the file and deletes
the scenario, exiting non-zero as it does — so a run that looks like it proved the point has in fact
disarmed the branch. Check `git diff` before committing, not just the exit code.

## Do not merge, and do not fix

The file is meant to stay broken. `mise run setup` installs prek's git hooks, after which a plain
`git commit` on this branch will strip the whitespace for you.

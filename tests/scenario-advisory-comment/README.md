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

Because without this branch, that half of `prek-advisory.yml` never runs. The other scenarios reach it
in neither direction:

- Three of them **pass** prek, so `failed` is `'false'` and the reporting steps no-op.
- [test/lockfile-drift](../scenario-lockfile-drift/README.md) fails at *Install from the lockfile*, before
  prek is reached at all, so `failed` is never set and the reporting steps are `skipped`.

So a green `advisory / prek-advisory` everywhere else means *prek ran*, never *the comment works*. Change
which token the step is handed, or typo the marker, and nothing else here would say so — the marker in
particular is not hypothetical: it changed once already, and the evidence is the orphaned comment recorded
below.

Choosing *trailing whitespace in Markdown* is the load-bearing part. `mise run lint` is
`uv run ruff check .`, and ruff does not look for it, so the blocking check stays green and the
advisory comment is the only report of the finding. That is the arrangement the upstream README claims
`prek-advisory.yml` exists to provide.

## Expected result

| Check | Expected | Why |
| --- | --- | --- |
| `ci / python-ci` | 💚 | `mise run lint` is ruff, which ignores trailing whitespace |
| `variants / python-ci` | ❤️ | `lint-changed-only` runs prek over the diff, and the broken file is in it |
| `advisory / prek-advisory` | 💚 **while reporting the failure** | the prek step's exit code is swallowed by `set +e`, so the job succeeds and comments |

The third row is the assertion, and the colour is the wrong thing to read it by: this scenario is the
one where a green check means the opposite of a passing lint.

`variants` going red is not a flaw in the scenario. A single pull request cannot break a file outside
its own diff, so the changed-files run necessarily sees what the all-files run sees. What the branch
demonstrates is therefore the *pair* of verdicts on one finding — blocking in the changed-files run,
advisory in the all-files run — rather than a finding only the advisory could have caught.

## Observed at `@v0.1`

PR #24, four pushes, every one with `advisory / prek-advisory` green and `Run prek on all files` failing
inside it.

```text
trim trailing whitespace.................................................Failed
- hook id: trailing-whitespace
- files were modified by this hook
  Fixing tests/scenario-advisory-comment/trailing-whitespace.md
```

The comment is one comment, and stayed one across all four:

| | First push | Fourth push |
| --- | --- | --- |
| comment id | `5654134497` | `5654134497` — unchanged |
| `created_at` | `15:15:58Z` | `15:15:58Z` — unchanged |
| `updated_at` | `15:15:58Z` | `18:13:08Z` — moved |
| `Details:` run | `34765059941` | `34773927707` — repointed |

Same id with a moved `updated_at` is the find-or-update branch; a second id would have been the
create branch firing twice. `created_at` staying put is what rules out delete-and-recreate.

### The marker changed across the version lines

PR #24 carries a **second** comment, id `5559031460`, created 2026-09-06 and last touched 2026-09-07.
It is not a second comment from this capability — it is the `@v4` one, orphaned.

`@v4` marked its comment `<!-- precommit-all-files-advisory -->`; this line marks it
`<!-- prek-advisory -->`, and the find step selects on that marker alone. So the current capability
cannot see the old comment, leaves it where it is, and creates its own.

The consequence is a consumer's, not this repository's: any pull request that already carried a `@v4`
advisory comment keeps it forever after repinning, beside a live one. Nothing breaks — the marker is not
an input, a check name or a permission, so it is absorbed by resolving the ref — but it is not
self-evident from the diff either, and a reader counting comments on this pull request will find two
where the assertion above says one.

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

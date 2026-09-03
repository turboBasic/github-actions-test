# Scenario inventory

This repository is the consumer that exercises
[`turboBasic/github-actions`](https://github.com/turboBasic/github-actions). Its workflows are called
from `.github/workflows/`, and each `test/scenario-*` branch pins a *different* caller-side
configuration — the shapes nothing inside `github-actions` can exercise itself, because its own
self-calls take the defaults.

**The branches are the artifacts; this file is the index.** A scenario lives on its branch, red or
green as its README says, and is never merged. Each README is mirrored here so the set can be read
without checking out five branches, and so a scenario cannot be quietly lost by deleting a branch
nobody remembered.

| Branch | Test scenario | Notes |
| --- | --- | --- |
| [`test/scenario-checks-disabled`](../../tree/test/scenario-checks-disabled) | `conventional-commits.yml` with `check-title: false` and `check-commits: false`. | **The most dangerous behaviour in the set.** Both checks report *success without running*, because GitHub counts a skipped job as passed — and a skipped **required** check satisfies the ruleset, so the branch is `MERGEABLE` with two gates that validated nothing. Drop a check and remove its required context in the same change. |
| [`test/scenario-custom-task-names`](../../tree/test/scenario-custom-task-names) | `python-ci.yml`'s `lint-task`, `typecheck-task` and `test-task`, with the repo's mise tasks renamed to `check`, `types` and `spec`. | Passes. The override path is never taken upstream, since `github-actions` self-calls with the defaults. Rename a task without wiring the input and the job fails with `task not found`. |
| [`test/scenario-lockfile-drift`](../../tree/test/scenario-lockfile-drift) | `python-ci.yml`'s `uv sync --locked`, with `[project].version` bumped to `0.2.0` and `uv.lock` left alone. | **Meant to stay red**, at *Sync dependencies*, before any lint or test runs. The surprising half is that a *version* bump counts as drift when no dependency changed. `github-actions` hit this cutting v2.0.2. Do not fix. |
| [`test/scenario-mise-version-pin`](../../tree/test/scenario-mise-version-pin) | `python-ci.yml`'s `mise-version`, pinned to `2026.9.0` and forwarded to `jdx/mise-action`. | Passes, but **the log line is the assertion**: the mise-action step must report `2026.9.0` rather than the newest release. A green job alone cannot tell a forwarded input from an ignored one. `opus-magnum` is the only real consumer that pins it. |
| [`test/scenario-stages-off`](../../tree/test/scenario-stages-off) | `python-ci.yml`'s `run-typecheck: false` and `run-tests: false`, with those tasks **deleted** from `mise.toml`. | Passes, running only checkout, `uv sync --locked` and `mise run lint`. Deleting the tasks is what makes it real — passing the inputs in a repo that *has* the tasks proves only that the `if:` works. This is `opus-magnum`'s actual shape. |

None of these branches is merged, and none should be. `main` holds the default call site — what a new
consumer copies out of the README — plus one variant call for the caller-side inputs.

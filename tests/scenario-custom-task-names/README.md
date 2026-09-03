# Scenario: custom mise task names

## What it exercises

`python-ci.yml`'s `lint-task`, `typecheck-task` and `test-task` inputs.

This branch renames the repo's mise tasks to `check`, `types` and `spec`, then passes those names in.
A consumer whose task names differ from the defaults has no other way to call this workflow.

## Why it is worth a branch

The three inputs exist for exactly one caller shape and nothing upstream can prove they work: the
defaults are what `github-actions` itself uses in its self-call, so the override path is never taken
there. Rename a task without wiring the input and the job fails with `task not found` — which is what
this branch would catch.

## Expected result

`ci / CI` **passes**, having run `mise run check`, `mise run types` and `mise run spec`.

Break the pairing — rename a task in `mise.toml` and not in `ci.yml` — and it fails at whichever
stage lost its task.

## Do not merge

`main` uses the default task names on purpose, because that is what a new consumer copies out of the
README. This branch exists to be looked at, not landed.

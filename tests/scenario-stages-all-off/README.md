# Scenario: every stage switched off

## What it exercises

`project-ci.yml`'s refusal when `run-lint`, `run-build`, `run-typecheck` and `run-test` are all `false`.

Four switches make "nothing on" reachable from a call site, and a job whose every step is skipped reports
success. The capability refuses that call instead.

## Why it is worth a branch

Because the alternative is invisible. Without the refusal this branch would be **green**, and it would
stay green: a required check passing over a component it never read, with no failing step to notice and
nothing in the log to contradict it. That is the shape principle VII exists for, and it is the one thing a
gate inside `github-actions` cannot demonstrate — its own tests can assert the `if:` condition, but only a
call site can show what the condition prevents.

It is also the switch combination a consumer arrives at by accident. Migrating a repository stage by
stage, turning each off until its task exists, ends here.

## Expected result

`python / project-ci` **fails**, at the first step, before the checkout:

```text
::error::project-ci was called with run-lint, run-build, run-typecheck and run-test all false, so it
has nothing to judge. Switch on the stages this component has, or drop the call and the context
requiring it together.
```

The tree is `main`'s and passes on every other branch, which is the point: nothing here is broken except
the call.

## Do not merge, and do not fix

Switching any stage back on turns this into [test/stages-off](../scenario-stages-off/README.md), which is
the green neighbour of this branch and covers the case where a repository genuinely lacks some stages.
This one covers the case where it claims to lack all of them.

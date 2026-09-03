# Scenario: a pinned mise release

## What it exercises

`python-ci.yml`'s `mise-version` input, which it forwards to `jdx/mise-action`'s `version`.

This branch pins `2026.9.0`. `docs/consumers.md` records `opus-magnum` as the only consumer that pins
it, so this is the second caller of that path and the only one that can be broken safely.

## Why it is worth a branch

The default is `""`, which means "let the action decide". Every other consumer takes that default, so
a change that stopped forwarding the input — a rename, a typo in the `with:` block — would break
`opus-magnum` alone, and only on its next run.

The input is also the reason `mise.toml` pins every tool: mise chooses the resolver, `mise.toml`
chooses the tools. Pinning one without the other still drifts.

## Expected result

`ci / CI` **passes**, and its mise-action step logs `2026.9.0` rather than the newest release. That
line in the log is the assertion — a green job alone does not distinguish a forwarded input from an
ignored one.

## Do not merge

`main` takes the default deliberately: a pin here would need bumping forever, and Renovate does not
manage a version inside a `with:` block.

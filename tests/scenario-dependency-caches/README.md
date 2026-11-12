# Scenario: consumer dependency caches

## What it exercises

`cache-fixture` calls `project-ci.yml@main` with UV, Cargo, Go and npm lockfiles in one component. Its `deps` task installs all four locked dependency sets, then `build` compiles the Rust and Go fixtures. The root `mise.toml` pins the Node and Rust toolchains used by npm and Cargo.

## Expected result

The first CI run has cache misses, installs the dependencies and saves the UV, Cargo registry, Cargo target, Go module, Go build and npm caches. A second run with the same lockfiles reports cache hits for each path and completes the same tasks.

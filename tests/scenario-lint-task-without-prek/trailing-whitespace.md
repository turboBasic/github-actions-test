# Deliberately broken

The line below ends in two spaces. Do not fix it, and do not run `mise run lint` locally with intent
to commit afterwards — the lint task is now the hook runner, `trailing-whitespace` is a fixing hook,
and a local run repairs this file and disarms the branch.

This line has trailing whitespace.  

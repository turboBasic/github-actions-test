# Deliberately broken

This file exists so that prek has something to fail on while `uv sync --locked`
succeeds. The next line ends in two spaces:

Trailing whitespace lives at the end of this line.  

Do not fix it, and note that `prek run` locally will: `trailing-whitespace` is a
fixing hook, so a local run repairs this file and the scenario with it. Restore the
two spaces before committing.

`advisory / prek-advisory` reporting this finding as a pull request comment is the
whole point of the branch.
A second push adds this line, also ending in two spaces, so prek still fails and
the comment has something to be updated *to*: a new run URL under the same id.  

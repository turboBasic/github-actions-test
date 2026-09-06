def describe() -> str:
    return "consumer of turboBasic/github-actions"


def pinned_major() -> str:
    return "v2"


# Touched by turboBasic/github-actions#110 verification: a breaking change *inside* the
# declared consumer surface, which release.yml must refuse under a non-major version.

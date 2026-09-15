from pydantic import BaseModel, Field


def describe() -> str:
    return "consumer of turboBasic/github-actions"


def pinned_major() -> str:
    return "v2"


def line() -> str:
    """The compatibility line this repository is pinned to."""
    return "v0.1"


# An external dependency, so the typecheck stage reads third-party types and the test stage runs code
# that needs `deps` to have installed from the lockfile first.
class Component(BaseModel):
    name: str
    stages: tuple[str, ...] = Field(min_length=1)


def root_component() -> Component:
    return Component(name="python", stages=("lint", "typecheck", "test"))

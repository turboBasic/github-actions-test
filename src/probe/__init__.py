from pydantic import BaseModel, Field, ValidationError


def describe() -> str:
    return "consumer of turboBasic/github-actions"


def pinned_major() -> str:
    return "v2"


def line() -> str:
    """The compatibility line this repository is pinned to."""
    return "v0.1"


# An external dependency, so the typecheck stage reads third-party types and the test stage exercises
# code that cannot run until `deps` has installed from the lockfile. A component declaring no stage is
# refused here for the same reason `project-ci` refuses a call with every stage off.
class Component(BaseModel):
    name: str
    stages: tuple[str, ...] = Field(min_length=1)


def root_component() -> Component:
    return Component(name="python", stages=("lint", "typecheck", "test"))


def refuses_a_component_with_no_stage() -> bool:
    try:
        Component(name="empty", stages=())
    except ValidationError:
        return True
    return False

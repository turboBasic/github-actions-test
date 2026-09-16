import pytest
from pydantic import ValidationError

from probe import Component, describe, pinned_major, root_component


def test_describe_names_the_upstream() -> None:
    assert "github-actions" in describe()


def test_pinned_major_is_the_tag_the_workflows_use() -> None:
    assert pinned_major() == "v2"


def test_the_root_component_declares_the_stages_its_call_site_leaves_on() -> None:
    assert root_component().stages == ("lint", "typecheck", "test")


def test_a_component_with_no_stage_is_refused() -> None:
    with pytest.raises(ValidationError):
        Component(name="empty", stages=())

from probe import describe, pinned_major


def test_describe_names_the_upstream() -> None:
    assert "github-actions" in describe()


def test_pinned_major_is_the_tag_the_workflows_use() -> None:
    assert pinned_major() == "v2"

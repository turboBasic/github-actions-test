from probe import describe


def test_describe_names_the_upstream() -> None:
    assert "github-actions" in describe()

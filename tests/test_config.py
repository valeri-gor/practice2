from types import SimpleNamespace
import pytest
from src.main import (
    build_dependency_graph,
    generate_d2_text,
    validate_arguments,
)


def test_valid_config():
    args = SimpleNamespace(
        package="A",
        repo="tests/test_repo.json",
        test_mode=True,
        output="graph.svg",
        ascii=True,
        max_depth=3,
    )
    validate_arguments(args)


def test_invalid_depth():
    args = SimpleNamespace(
        package="A",
        repo="tests/test_repo.json",
        test_mode=True,
        output="graph.svg",
        ascii=False,
        max_depth=0,
    )
    with pytest.raises(ValueError):
        validate_arguments(args)


def test_d2_generation():
    repo = {"A": ["B", "C"], "B": [], "C": []}
    graph, _ = build_dependency_graph("A", 2, lambda p: repo.get(p, []))
    d2_out = generate_d2_text(graph)
    assert '"A" -> "B"' in d2_out
    assert '"A" -> "C"' in d2_out

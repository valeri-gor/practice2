from types import SimpleNamespace
import pytest
from src.main import (
    build_dependency_graph,
    get_load_order,
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


def test_dfs_and_load_order():
    repo = {"A": ["B"], "B": ["C", "D"], "C": ["B"], "D": []}
    graph, cycles = build_dependency_graph("A", 3, lambda p: repo.get(p, []))
    order = get_load_order("A", graph)
    assert cycles == [("C", "B")]
    assert order[-1] == "A"
    assert order.index("D") < order.index("B")

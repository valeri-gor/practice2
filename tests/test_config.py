from types import SimpleNamespace
import pytest
from src.main import build_dependency_graph, validate_arguments


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


def test_dfs_with_cycles_and_depth():
    repo = {"A": ["B"], "B": ["C", "D"], "C": ["B"], "D": []}
    graph, cycles = build_dependency_graph("A", 3, lambda p: repo.get(p, []))
    assert graph == {"A": ["B"], "B": ["C", "D"], "C": ["B"], "D": []}
    assert cycles == [("C", "B")]

from types import SimpleNamespace
import pytest
from src.main import validate_arguments


def test_valid_config():
    args = SimpleNamespace(
        package="express",
        repo="https://npmjs.org",
        test_mode=False,
        output="graph.svg",
        ascii=True,
        max_depth=3,
    )
    validate_arguments(args)


def test_invalid_depth():
    args = SimpleNamespace(
        package="express",
        repo="https://npmjs.org",
        test_mode=False,
        output="graph.svg",
        ascii=False,
        max_depth=0,
    )
    with pytest.raises(ValueError):
        validate_arguments(args)

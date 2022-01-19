import pytest

from project.graph_query_language.interpreter.gql_exceptions import (
    NotImplementedException,
)
from project.graph_query_language.interpreter.gql_types.bool import Bool
from tests.graph_query_language.interpreter.interpreter import interpreter_with_value


@pytest.mark.parametrize(
    "bool_expr, expected",
    [
        ("true & false", False),
        ("true & true", True),
        ("false & true", False),
        ("false & false", False),
    ],
)
def test_bool_intersect(bool_expr, expected):
    assert interpreter_with_value(bool_expr, "expr") == Bool(expected)


@pytest.mark.parametrize(
    "bool_expr, expected",
    [
        ("true | false", True),
        ("true | true", True),
        ("false | true", True),
        ("false | false", False),
    ],
)
def test_bool_union(bool_expr, expected):
    assert interpreter_with_value(bool_expr, "expr") == Bool(expected)


@pytest.mark.parametrize(
    "bool_expr, expected",
    [
        ("not true", False),
        ("not false", True),
    ],
)
def test_bool_inverse(bool_expr, expected):
    assert interpreter_with_value(bool_expr, "expr") == Bool(expected)


@pytest.mark.parametrize(
    "bool_expr",
    [
        "true . true",
        "true . false",
        "false . true",
        "false . false",
        "true *",
    ],
)
def test_bool_unsupported(bool_expr):
    with pytest.raises(NotImplementedException):
        interpreter_with_value(bool_expr, "expr")

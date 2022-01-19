import sys

import pytest

from project.graph_query_language.interpreter.gql_exceptions import (
    NotImplementedException,
    GQLTypeError,
)
from project.graph_query_language.interpreter.gql_types.set import Set

if sys.platform.startswith("win"):
    pytest.skip("Skip set tests", allow_module_level=True)
else:
    from tests.graph_query_language.interpreter.interpreter import (
        interpreter_with_value,
    )


@pytest.mark.parametrize(
    "set_expr, expected",
    [
        ("{1, 2, 3} & {2, 3, 4}", {2, 3}),
        ("{10, 11} & {}", set()),
        ("{} & {10, 22, 33, 44}", set()),
        ("{} & {}", set()),
        ("{10, 11, 12} & {20, 21, 22}", set()),
    ],
)
def test_set_intersect(set_expr, expected):
    actual_set = interpreter_with_value(set_expr, "expr")
    expected_set = Set(expected)
    assert actual_set.data == expected_set.data


@pytest.mark.parametrize(
    "set_expr, expected",
    [
        ("{1, 2, 3} | {2, 3, 4}", {1, 2, 3, 4}),
        ("{10, 11} | {}", {10, 11}),
        ("{} | {10, 22, 33, 44}", {10, 22, 33, 44}),
        ("{} | {}", set()),
        ("{10, 11, 12} | {20, 21, 22}", {10, 11, 12, 20, 21, 22}),
    ],
)
def test_set_union(set_expr, expected):
    actual_set = interpreter_with_value(set_expr, "expr")
    expected_set = Set(expected)
    assert actual_set.data == expected_set.data


@pytest.mark.parametrize(
    "set_expr",
    [
        "{10, 11} . {5, 7, 9}",
        "{} . {5, 7, 9}",
        "{10, 11} . {}",
        "not {10, 11}",
        "{1,2,3} *",
    ],
)
def test_set_unsupported(set_expr):
    with pytest.raises(NotImplementedException):
        interpreter_with_value(set_expr, "expr")


@pytest.mark.parametrize(
    "set_expr",
    [
        '{0, 1} & {"0", "1"}',
        '{0, 1} | {"0", "1"}',
    ],
)
def test_set_type_error(set_expr):
    with pytest.raises(GQLTypeError):
        interpreter_with_value(set_expr, "expr")


@pytest.mark.parametrize(
    "range_expr, expected",
    [
        ("{11..14}", {11, 12, 13, 14}),
        ("{1..1}", {1}),
    ],
)
def test_vertices_range(range_expr, expected):
    actual_set = interpreter_with_value(range_expr, "vertices_range")
    assert actual_set.data == Set(expected).data


def test_set_type_consistency():
    with pytest.raises(GQLTypeError):
        Set.fromSet({1, "1"})

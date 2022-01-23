import pytest

from project import regex_to_min_dfa
from tests.graph_query_language.interpreter.interpreter import (
    interpreter_with_value,
)


@pytest.mark.parametrize(
    "lhs, op, rhs, expected",
    [
        ('"l1" & "l1"', "&", '"l1" | "l1"', '"l1"'),
        ('"l1" | "l2"', "|", '"l2" | "l3"', '"l1" | "l2" | "l3"'),
    ],
)
def test_finite_automata_intersection(lhs, op, rhs, expected):
    expression = lhs + " " + op + " " + rhs
    actual = interpreter_with_value(expression, "expr")
    expected = regex_to_min_dfa(expected)
    assert actual.nfa.is_equivalent_to(expected)

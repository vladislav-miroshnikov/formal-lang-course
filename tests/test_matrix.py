import pytest
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton

from project import BooleanMatrices


@pytest.fixture
def nfa():
    nfa = NondeterministicFiniteAutomaton()
    nfa.add_transitions(
        [
            (0, "X", 1),
            (0, "X", 2),
            (1, "Y", 2),
            (1, "Z", 1),
            (2, "S", 3),
            (3, "W", 4),
            (4, "W", 0),
        ]
    )

    return nfa


@pytest.mark.parametrize(
    "label,expected_nnz", [("X", 2), ("Y", 1), ("Z", 1), ("S", 1), ("W", 2)]
)
def test_nonzero(nfa, label, expected_nnz):
    bm = BooleanMatrices(nfa)
    actual_nnz = bm.bool_matrices[label].nnz

    assert actual_nnz == expected_nnz


def test_symbols(nfa):
    bm = BooleanMatrices(nfa)
    actual_symbols = bm.bool_matrices.keys()
    expected_symbols = nfa.symbols

    assert actual_symbols == expected_symbols


@pytest.mark.parametrize(
    "label,edges",
    [
        ("X", [(0, 1), (0, 2)]),
        ("Y", [(1, 2)]),
        ("Z", [(1, 1)]),
        ("S", [(2, 3)]),
        ("W", [(3, 4), (4, 0)]),
    ],
)
def test_adjacency(nfa, label, edges):
    bm = BooleanMatrices(nfa)
    assert all(bm.bool_matrices[label][edge] for edge in edges)


def test_transitive_closure(nfa):
    bm = BooleanMatrices(nfa)
    tc = bm.make_transitive_closure()
    assert tc.sum() == tc.size

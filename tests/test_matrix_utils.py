from pyformlang.finite_automaton import (
    NondeterministicFiniteAutomaton,
    State,
    DeterministicFiniteAutomaton,
)

from project import BooleanMatrices, intersect_boolean_matrices, convert_bm_to_automaton


def test_intersection():
    fa1 = NondeterministicFiniteAutomaton()
    fa1.add_transitions(
        [(0, "X", 1), (0, "Y", 1), (0, "Z", 0), (1, "Y", 1), (1, "Z", 2), (2, "S", 0)]
    )
    fa1.add_start_state(State(0))
    fa1.add_final_state(State(0))
    fa1.add_final_state(State(1))
    fa1.add_final_state(State(2))

    bm1 = BooleanMatrices(fa1)

    fa2 = NondeterministicFiniteAutomaton()
    fa2.add_transitions([(0, "X", 1), (0, "X", 0), (1, "Y", 1), (1, "W", 2)])
    fa2.add_start_state(State(0))
    fa2.add_final_state(State(1))

    bm2 = BooleanMatrices(fa2)

    expected_fa = DeterministicFiniteAutomaton()
    expected_fa.add_transitions([(0, "X", 1), (1, "Y", 1)])
    expected_fa.add_start_state(State(0))
    expected_fa.add_final_state(State(1))

    intersected_bm = intersect_boolean_matrices(bm1, bm2)

    actual_fa = convert_bm_to_automaton(intersected_bm)

    assert actual_fa.is_equivalent_to(expected_fa)

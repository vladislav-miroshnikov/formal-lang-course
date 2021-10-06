from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State
from scipy import sparse

from project.matrix import BooleanMatrices

__all__ = ["intersect_boolean_matrices", "convert_bm_to_automaton"]


def intersect_boolean_matrices(self: BooleanMatrices, other: BooleanMatrices):
    """
    Makes intersection of self boolean matrix with other

    Parameters
    ----------
    self: BooleanMatrices
        Left-hand side boolean matrix
    other: BooleanMatrices
        Right-hand side boolean matrix

    Returns
    -------
    intersect_bm: BooleanMatrices
        Intersection of two boolean matrices
    """
    intersect_bm = BooleanMatrices()
    intersect_bm.num_states = self.states_count * other.states_count
    common_symbols = self.bool_matrices.keys() & other.bool_matrices.keys()

    for symbol in common_symbols:
        intersect_bm.bool_matrices[symbol] = sparse.kron(
            self.bool_matrices[symbol], other.bool_matrices[symbol], format="csr"
        )

    for state_fst, state_fst_index in self.state_indices.items():
        for state_snd, state_snd_idx in other.state_indices.items():
            new_state = new_state_idx = (
                state_fst_index * other.states_count + state_snd_idx
            )
            intersect_bm.state_indices[new_state] = new_state_idx

            if state_fst in self.start_states and state_snd in other.start_states:
                intersect_bm.start_states.add(new_state)

            if state_fst in self.final_states and state_snd in other.final_states:
                intersect_bm.final_states.add(new_state)

    return intersect_bm


def convert_bm_to_automaton(boolean_matrices: BooleanMatrices):
    """
    Converts BooleanMatrices to NFA

    Returns
    -------
    automaton: NondeterministicFiniteAutomaton
        Representation of BooleanMatrices as NFA
    """
    automaton = NondeterministicFiniteAutomaton()
    for label, bool_matrix in boolean_matrices.bool_matrices.items():
        for state_from, state_to in zip(*bool_matrix.nonzero()):
            automaton.add_transition(state_from, label, state_to)

    for state in boolean_matrices.start_states:
        automaton.add_start_state(State(state))

    for state in boolean_matrices.final_states:
        automaton.add_final_state(State(state))

    return automaton

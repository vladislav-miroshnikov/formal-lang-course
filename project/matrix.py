from pyformlang.cfg import Variable
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State
from scipy import sparse

__all__ = ["BooleanMatrices"]

from scipy.sparse import dok_matrix

from project.rsm import RSM, Box


class BooleanMatrices:
    """
    Representation of NFA as a Boolean Matrix

    Attributes
    ----------
    states_count: set
        Count of states
    state_indices: dict
        Dictionary of states
    start_states: set
        Start states of NFA
    final_states: set
        Final states of NFA
    bool_matrices: dict
        Dictionary of boolean matrices.
        Keys are NFA symbols
    """

    def __init__(self, n_automaton: NondeterministicFiniteAutomaton = None):
        if n_automaton is None:
            self.states_count = 0
            self.state_indices = dict()
            self.start_states = set()
            self.final_states = set()
            self.bool_matrices = dict()
            self.states_to_box_variable = {}
        else:
            self.states_count = len(n_automaton.states)
            self.state_indices = {
                state: index for index, state in enumerate(n_automaton.states)
            }
            self.start_states = n_automaton.start_states
            self.final_states = n_automaton.final_states
            self.bool_matrices = self.init_bool_matrices(n_automaton)
            self.states_to_box_variable = {}

    def get_states(self):
        return self.state_indices.keys()

    def get_start_states(self):
        return self.start_states

    def get_final_states(self):
        return self.final_states

    def init_bool_matrices(self, n_automaton: NondeterministicFiniteAutomaton):
        """
        Initialize boolean matrices of NondeterministicFiniteAutomaton

        Parameters
        ----------
        n_automaton: NondeterministicFiniteAutomaton
            NFA to transform to matrix

        Returns
        -------
        bool_matrices: dict
            Dict of boolean matrix for every automata label-key
        """
        bool_matrices = dict()
        nfa_dict = n_automaton.to_dict()
        for state_from, trans in nfa_dict.items():
            for label, states_to in trans.items():
                if not isinstance(states_to, set):
                    states_to = {states_to}
                for state_to in states_to:
                    index_from = self.state_indices[state_from]
                    index_to = self.state_indices[state_to]
                    if label not in bool_matrices:
                        bool_matrices[label] = sparse.dok_matrix(
                            (self.states_count, self.states_count), dtype=bool
                        )
                    bool_matrices[label][index_from, index_to] = True

        return bool_matrices

    def make_transitive_closure(self):
        """
        Makes transitive closure of boolean matrices

        Returns
        -------
        tc: dok_matrix
            Transitive closure of boolean matrices
        """
        if not self.bool_matrices.values():
            return dok_matrix((1, 1))

        tc = sum(self.bool_matrices.values())
        prev_nnz = tc.nnz
        curr_nnz = 0

        while prev_nnz != curr_nnz:
            tc += tc @ tc
            prev_nnz, curr_nnz = curr_nnz, tc.nnz

        return tc

    @classmethod
    def from_rsm(cls, rsm: RSM):
        """
        Create an instance of BooleanMatrices from rsm

        Attributes
        ----------
        rsm: RSM
            Recursive State Machine
        """
        bm = cls()
        bm.states_count = sum(len(box.dfa.states) for box in rsm.boxes)
        box_idx = 0
        for box in rsm.boxes:
            for idx, state in enumerate(box.dfa.states):
                new_name = bm._rename_rsm_box_state(state, box.variable)
                bm.state_indices[new_name] = idx + box_idx
                if state in box.dfa.start_states:
                    bm.start_states.add(bm.state_indices[new_name])
                if state in box.dfa.final_states:
                    bm.final_states.add(bm.state_indices[new_name])

            bm.states_to_box_variable.update(
                {
                    (
                        bm.state_indices[
                            bm._rename_rsm_box_state(box.dfa.start_state, box.variable)
                        ],
                        bm.state_indices[bm._rename_rsm_box_state(state, box.variable)],
                    ): box.variable.value
                    for state in box.dfa.final_states
                }
            )
            bm.bool_matrices.update(bm._create_box_bool_matrices(box))
            box_idx += len(box.dfa.states)

        return bm

    @staticmethod
    def _rename_rsm_box_state(state: State, box_variable: Variable):
        return State(f"{state.value}#{box_variable.value}")

    def _create_box_bool_matrices(self, box: Box) -> dict:
        """
        Create bool matrices for RSM box
        Attributes
        ----------
        box: Box
            Box of RSM
        Returns
        -------
        bmatrix: dict
            Boolean Matrices dict
        """
        bmatrix = {}
        for s_from, trans in box.dfa.to_dict().items():
            for label, states_to in trans.items():
                if not isinstance(states_to, set):
                    states_to = {states_to}
                for s_to in states_to:
                    idx_from = self.state_indices[
                        self._rename_rsm_box_state(s_from, box.variable)
                    ]
                    idx_to = self.state_indices[
                        self._rename_rsm_box_state(s_to, box.variable)
                    ]

                    if label in self.bool_matrices:
                        self.bool_matrices[label][idx_from, idx_to] = True
                        continue
                    if label not in bmatrix:
                        bmatrix[label] = sparse.dok_matrix(
                            (self.states_count, self.states_count), dtype=bool
                        )
                    bmatrix[label][idx_from, idx_to] = True

        return bmatrix

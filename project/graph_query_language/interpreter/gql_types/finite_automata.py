from networkx import MultiDiGraph
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton

from project.graph_funcs import get_nfa_by_graph, add_states_to_nfa, replace_nfa_states
from project.graph_query_language.interpreter.gql_exceptions import (
    NotImplementedException,
)
from project.graph_query_language.interpreter.gql_types.base_automata import (
    BaseAutomata,
)
from project.matrix import BooleanMatrices
from project.matrix_utils import convert_bm_to_automaton, intersect_boolean_matrices


class FiniteAutomata(BaseAutomata):
    def __init__(self, nfa: NondeterministicFiniteAutomaton):
        self.nfa = nfa

    def __str__(self):
        return str(self.nfa.to_dict())

    @classmethod
    def fromGraph(cls, graph: MultiDiGraph):
        return cls(nfa=get_nfa_by_graph(graph))

    def intersect(self, other: "FiniteAutomata"):
        lhs = BooleanMatrices(self.nfa)
        rhs = BooleanMatrices(other.nfa)
        intersection_result = intersect_boolean_matrices(lhs, rhs)
        return FiniteAutomata(convert_bm_to_automaton(intersection_result))

    def union(self, other: "FiniteAutomata"):
        return FiniteAutomata(self.nfa.union(other.nfa).to_deterministic())

    def concatenate(self, other: "FiniteAutomata"):
        lhs = self.nfa.to_regex()
        rhs = other.nfa.to_regex()
        return FiniteAutomata(lhs.concatenate(rhs).to_epsilon_nfa().to_deterministic())

    def inverse(self):
        inverse_nfa = self.nfa.copy()
        for state in inverse_nfa.states:
            inverse_nfa.add_final_state(state)
        for state in self.nfa.final_states:
            inverse_nfa.remove_final_state(state)
        return FiniteAutomata(nfa=inverse_nfa)

    def kleene(self):
        return FiniteAutomata(nfa=self.nfa.kleene_star().to_deterministic())

    @property
    def start(self):
        return self.nfa.start_states

    @property
    def final(self):
        return self.nfa.final_states

    @property
    def symbols(self):
        return self.nfa.symbols

    @property
    def transitions(self):
        return self.nfa.to_dict()

    @property
    def states(self):
        return self.nfa.states

    def set_start(self, start_states):
        self.nfa = replace_nfa_states(self.nfa, start_states=start_states)

    def set_final(self, final_states):
        self.nfa = replace_nfa_states(self.nfa, final_states=final_states)

    def add_start(self, start_states):
        self.nfa = add_states_to_nfa(self.nfa, start_states=start_states)

    def add_final(self, final_states):
        self.nfa = add_states_to_nfa(self.nfa, final_states=final_states)

    def get_reachable(self):
        raise NotImplementedException("")

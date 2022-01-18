from networkx import MultiDiGraph
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton

from project.graph_funcs import get_nfa_by_graph, add_states_to_nfa, replace_nfa_states
from project.graph_query_language.interpreter.gql_exceptions import (
    NotImplementedException,
)
from project.graph_query_language.interpreter.gql_types.base_automata import (
    BaseAutomata,
)
from project.graph_query_language.interpreter.gql_types.set import (
    Set,
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
        return Set(self.nfa.start_states)

    @property
    def final(self):
        return Set(self.nfa.final_states)

    @property
    def labels(self):
        return Set(self.nfa.symbols)

    @property
    def edges(self):
        edges_dict = self.nfa.to_dict()
        edges_set = set()
        for u in edges_dict.keys():
            for label, v_s in edges_dict.get(u).items():
                for v in v_s:
                    edges_set.add((u, label, v))
        return Set(edges_set)

    @property
    def vertices(self):
        return Set(self.nfa.states)

    def set_start(self, start_states: Set):
        self.nfa = replace_nfa_states(self.nfa, start_states=start_states.data)

    def set_final(self, final_states: Set):
        self.nfa = replace_nfa_states(self.nfa, final_states=final_states.data)

    def add_start(self, start_states: Set):
        self.nfa = add_states_to_nfa(self.nfa, start_states=start_states.data)

    def add_final(self, final_states: Set):
        self.nfa = add_states_to_nfa(self.nfa, final_states=final_states.data)

    def get_reachable(self):
        raise NotImplementedException("")

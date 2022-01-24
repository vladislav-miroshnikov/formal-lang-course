from networkx import MultiDiGraph
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.regular_expression import MisformedRegexError

from project import regex_to_min_dfa
from project.graph_funcs import get_nfa_by_graph, add_states_to_nfa, replace_nfa_states
from project.graph_query_language.interpreter.gql_exceptions import (
    InvalidCastException,
    GQLTypeError,
)
from project.graph_query_language.interpreter.gql_types.base_automata import (
    BaseAutomata,
)
from project.graph_query_language.interpreter.gql_types.gql_cfg import GqlCFG
from project.graph_query_language.interpreter.gql_types.set import (
    Set,
)
from project.matrix import BooleanMatrices
from project.matrix_utils import convert_bm_to_automaton, intersect_boolean_matrices
from project.rpq import get_reachable


class FiniteAutomata(BaseAutomata):
    """
    Gql type of Finite Automata

    Attributes
    ----------
    nfa: NondeterministicFiniteAutomaton
        Internal nfa object
    """

    def __init__(self, nfa: NondeterministicFiniteAutomaton):
        self.nfa = nfa

    def __str__(self):
        return str(self.nfa.minimize().to_regex())

    @staticmethod
    def __get_reachable(nfa: NondeterministicFiniteAutomaton) -> set:
        """
        Internal function to get reachable vertices set

        Parameters
        ----------
        nfa: NondeterministicFiniteAutomaton
            Finite Automata

        Returns
        -------
        reachable: set
            Reachable vertices set
        """
        bmatrix = BooleanMatrices(nfa)
        return get_reachable(bmatrix)

    @classmethod
    def fromGraph(cls, graph: MultiDiGraph) -> "FiniteAutomata":
        """
        Parameters
        ----------
        graph: MultiDiGraph
            Transform graph into automata

        Returns
        -------
        fa: FiniteAutomata
            Automata transformed from graph
        """
        return cls(nfa=get_nfa_by_graph(graph))

    @classmethod
    def fromString(cls, regex_str: str) -> "FiniteAutomata":
        """
        Parameters
        ----------
        regex_str: str
            Transform regular-expression string into automata

        Returns
        -------
        fa: FiniteAutomata
            Automata transformed from string

        Raises
        ------
        InvalidCastException
            If given string violates regular expression rules
        """
        try:
            return FiniteAutomata(nfa=regex_to_min_dfa(regex_str))
        except MisformedRegexError as exc:
            raise InvalidCastException("str", "regex") from exc

    def __intersectFiniteAutomata(self, other: "FiniteAutomata") -> "FiniteAutomata":
        """
        Inner intersection (FiniteAutomata & FiniteAutomata) function

        Parameters
        ----------
        other: FiniteAutomata
            Finite Automata

        Returns
        -------
        intersection: FiniteAutomata
            Intersection of two FA
        """
        lhs = BooleanMatrices(self.nfa)
        rhs = BooleanMatrices(other.nfa)
        intersection_result = intersect_boolean_matrices(lhs, rhs)
        return FiniteAutomata(
            nfa=convert_bm_to_automaton(intersection_result),
        )

    def __intersectCFG(self, other: GqlCFG) -> GqlCFG:
        """
        Inner intersection (FiniteAutomata & GqlCFG) function

        Parameters
        ----------
        other: GqlCFG
            Context Free Grammar

        Returns
        -------
        intersection: GqlCFG
            Intersection of FiniteAutomata with GqlCFG
        """
        intersection = other.intersect(self)
        return intersection

    def intersect(self, other) -> "BaseAutomata":
        """
        Automata & Automata intersection

        Parameters
        ----------
        other: GqlCFG | FiniteAutomata
            GqlCFG or FiniteAutomata object

        Returns
        -------
        intersection: BaseAutomata
            cfg, IF 'other' is GqlCFG
            fa, IF 'other' is FiniteAutomata

        Raises
        ------
        GQLTypeError
            If object does not represent FiniteAutomata or GqlCFG
        """
        if isinstance(other, FiniteAutomata):
            return self.__intersectFiniteAutomata(other=other)

        if isinstance(other, GqlCFG):
            return self.__intersectCFG(other=other)

        raise GQLTypeError(
            f"Expected type BaseAutomata, got {str(type(other))} instead."
        )

    def union(self, other: "FiniteAutomata") -> "FiniteAutomata":
        """
        Union of two FiniteAutomata

        Parameters
        ----------
        other: FiniteAutomata
            rhs FA

        Returns
        -------
        union: FiniteAutomata
            Union of two FA
        """
        return FiniteAutomata(self.nfa.union(other.nfa).to_deterministic())

    def concatenate(self, other: "FiniteAutomata") -> "FiniteAutomata":
        """
        Concatenate of two FiniteAutomata

        Parameters
        ----------
        other: FiniteAutomata
            rhs FA

        Returns
        -------
        concatenate: FiniteAutomata
            Concatenate of two FA
        """
        lhs = self.nfa.to_regex()
        rhs = other.nfa.to_regex()
        return FiniteAutomata(lhs.concatenate(rhs).to_epsilon_nfa().to_deterministic())

    def inverse(self) -> "FiniteAutomata":
        """
        Get complement of FiniteAutomata

        Returns
        -------
        complement: FiniteAutomata
            Complement of FA
        """
        return FiniteAutomata(self.nfa.get_complement().to_deterministic())

    def kleene(self) -> "FiniteAutomata":
        """
        Kleene closure of FiniteAutomata

        Returns
        -------
        kleene: FiniteAutomata
            Kleene closure of FA
        """
        return FiniteAutomata(nfa=self.nfa.kleene_star().to_deterministic())

    @property
    def start(self) -> Set:
        return Set(self.nfa.start_states)

    @property
    def final(self) -> Set:
        return Set(self.nfa.final_states)

    @property
    def labels(self) -> Set:
        return Set(self.nfa.symbols)

    @property
    def edges(self) -> Set:
        edges_dict = self.nfa.to_dict()
        edges_set = set()
        for u in edges_dict.keys():
            for label, v_s in edges_dict.get(u).items():
                for v in v_s:
                    edges_set.add((u, label, v))
        return Set(edges_set)

    @property
    def vertices(self) -> Set:
        return Set(self.nfa.states)

    def set_start(self, start_states: Set) -> "FiniteAutomata":
        nfa = replace_nfa_states(self.nfa, start_states=start_states.data)
        return FiniteAutomata(nfa)

    def set_final(self, final_states: Set) -> "FiniteAutomata":
        nfa = replace_nfa_states(self.nfa, final_states=final_states.data)
        return FiniteAutomata(nfa)

    def add_start(self, start_states: Set) -> "FiniteAutomata":
        nfa = add_states_to_nfa(self.nfa, start_states=start_states.data)
        return FiniteAutomata(nfa)

    def add_final(self, final_states: Set) -> "FiniteAutomata":
        nfa = add_states_to_nfa(self.nfa, final_states=final_states.data)
        return FiniteAutomata(nfa)

    def get_reachable(self) -> Set:
        """
        Returns
        -------
        reachable: Set
            Reachable vertices set
        """
        return Set(FiniteAutomata.__get_reachable(self.nfa))

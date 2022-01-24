from pyformlang.cfg import CFG

from project import convert_cfg_to_ecfg, convert_ecfg_to_rsm, BooleanMatrices
from project.graph_query_language.interpreter.gql_exceptions import (
    NotImplementedException,
    InvalidCastException,
    GQLTypeError,
)
from project.graph_query_language.interpreter.gql_types.base_automata import (
    BaseAutomata,
)
from project.graph_query_language.interpreter.gql_types.set import Set


class GqlCFG(BaseAutomata):
    """
    GQL class for Context-Free-Grammar

    Attributes
    ----------
    cfg: CFG
        Internal CFG object
    """

    def __init__(self, cfg: CFG):
        self.cfg = cfg

    def __str__(self):
        return self.cfg.to_text()

    @classmethod
    def fromText(cls, text: str) -> "GqlCFG":
        """
        Parameters
        ----------
        text: str
            String given in terms of CFG
            E.g. 'S -> a S
                  S -> epsilon'

        Returns
        -------
        cfg: GqlCFG
            Object transformed from text

        Raises
        ------
        InvalidCastException
            If text can't convert to CFG format
        """
        try:
            cfg = CFG.from_text(text=text)
            return cls(cfg=cfg)
        except ValueError as e:
            raise InvalidCastException("str", "CFG") from e

    def intersect(self, other: BaseAutomata) -> "GqlCFG":
        """
        Parameters
        ----------
        other: FiniteAutomata
            GQL Finite automata

        Returns
        -------
        intersection: GqlCFG
            Intersection of CFG and FiniteAutomata

        Raises
        ------
        GQLTypeError
            If 'other' type is not FiniteAutomata
        """
        if not isinstance(other, BaseAutomata):
            raise GQLTypeError(
                f"Expected type FiniteAutomata, got {str(type(other))} instead."
            )

        if isinstance(other, GqlCFG):
            raise GQLTypeError("GqlCFG cannot intersect with another GqlCFG")

        intersection = self.cfg.intersection(other.nfa)

        return GqlCFG(cfg=intersection)

    def union(self, other) -> "GqlCFG":
        """
        Union of CFG with another CFG

        Parameters
        ----------
        other: GqlCFG
            GqlCFG object

        Returns
        -------
        union: GqlCFG
            Union of two CFG
        """
        if isinstance(other, GqlCFG):
            return GqlCFG(cfg=self.cfg.union(other.cfg))

        raise NotImplementedException("Union supported only GqlCFG types")

    def concatenate(self, other) -> "GqlCFG":
        """
        Concatenation of CFG with another CFG

        Parameters
        ----------
        other: GqlCFG
            GqlCFG object

        Returns
        -------
        concatenation: GqlCFG
            Concatenation of two CFG
        """
        if isinstance(other, GqlCFG):
            return GqlCFG(cfg=self.cfg.concatenate(other.cfg))

        raise NotImplementedException("Concatenate supported only GqlCFG types")

    def inverse(self):
        raise NotImplementedException("GqlCFG doesn't support inverse operation")

    def kleene(self):
        raise NotImplementedException("GqlCFG doesn't support kleene operation")

    def set_start(self, start_states):
        raise NotImplementedException(
            "Start symbol can't be set to GqlCFG after creation"
        )

    def set_final(self, final_states):
        raise NotImplementedException("Final symbol can't be set to GqlCFG")

    def add_start(self, start_states):
        raise NotImplementedException("Start symbols can't be added to GqlCFG")

    def add_final(self, final_states):
        raise NotImplementedException("Final symbols can't be added to GqlCFG")

    @property
    def start(self) -> Set:
        return Set(self.cfg.start_symbol.value)

    @property
    def final(self) -> Set:
        return Set(set(self.cfg.get_reachable_symbols()))

    @property
    def labels(self) -> Set:
        return Set(set(self.cfg.terminals))

    @property
    def edges(self) -> Set:
        raise NotImplementedException("GqlCFG edges doesn't support")

    @property
    def vertices(self) -> Set:
        return Set(set(self.cfg.variables))

    def get_reachable(self) -> Set:
        """
        Get reachable vertices from the start

        Returns
        -------
        reachable: Set
            Set of reachable vertices
        """
        ecfg = convert_cfg_to_ecfg(self.cfg)
        rsm = convert_ecfg_to_rsm(ecfg)
        rsm_bm = BooleanMatrices.from_rsm(rsm)
        tc = rsm_bm.make_transitive_closure()
        reachable = set()
        for i, j in zip(*tc.nonzero()):
            reachable.add((i, rsm_bm.states_to_box_variable.get((i, j)), j))

        return Set(reachable)

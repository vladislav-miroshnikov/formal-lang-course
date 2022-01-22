from pyformlang.cfg import CFG

from project.graph_query_language.interpreter.gql_exceptions import (
    NotImplementedException,
    InvalidCastException,
)
from project.graph_query_language.interpreter.gql_types.base_automata import (
    BaseAutomata,
)
from project.graph_query_language.interpreter.gql_types.finite_automata import (
    FiniteAutomata,
)
from project.graph_query_language.interpreter.gql_types.set import Set


class RSM(BaseAutomata):
    def __init__(self, cfg: CFG):
        self.cfg = cfg
        self.reachable = None

    def __str__(self):
        return self.cfg.to_text()

    @classmethod
    def fromText(cls, text: str):
        try:
            cfg = CFG.from_text(text=text)
            return cls(cfg=cfg)
        except ValueError as e:
            raise InvalidCastException("str", "CFG") from e

    def intersect(self, other):
        if isinstance(other, FiniteAutomata):
            intersection = self.cfg.to_pda().intersection(other.nfa)
        else:
            raise InvalidCastException("CFG cannot intersect with ", str(type(other)))

        return CFG(cfg=intersection.to_cfg())

    def union(self, other):
        if isinstance(other, CFG):
            return CFG(cfg=self.cfg.union(other.cfg))

        raise NotImplementedException("Union supported only CFG types")

    def concatenate(self, other):
        if isinstance(other, CFG):
            return CFG(cfg=self.cfg.concatenate(other.cfg))

        raise NotImplementedException("Concatenate supported only CFG types")

    def inverse(self):
        raise NotImplementedException("CFG doesn't support inverse operation")

    def kleene(self):
        raise NotImplementedException("CFG doesn't support kleene operation")

    def set_start(self, start_states):
        pass

    def set_final(self, final_states):
        pass

    def add_start(self, start_states):
        pass

    def add_final(self, final_states):
        pass

    @property
    def start(self):
        return Set(set(self.cfg.start_symbol.to_text()))

    @property
    def final(self):
        raise NotImplementedException("CFG final doesn't support")

    @property
    def labels(self):
        raise NotImplementedException("CFG labels doesn't support")

    @property
    def edges(self):
        raise NotImplementedException("CFG edges doesn't support")

    @property
    def vertices(self):
        return Set(set(self.cfg.variables))

    def get_reachable(self):
        raise NotImplementedException("CFG reachable doesn't support")

from pyformlang.cfg import CFG

from project import convert_cfg_to_ecfg, convert_ecfg_to_rsm, BooleanMatrices
from project.graph_query_language.interpreter.gql_exceptions import (
    NotImplementedException,
    InvalidCastException,
)
from project.graph_query_language.interpreter.gql_types.base_automata import (
    BaseAutomata,
)
from project.graph_query_language.interpreter.gql_types.set import Set


class GqlCFG(BaseAutomata):
    def __init__(self, cfg: CFG):
        self.cfg = cfg

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
        if not isinstance(other, BaseAutomata):
            raise InvalidCastException("GqlCFG cannot intersect with", str(type(other)))

        if isinstance(other, GqlCFG):
            raise InvalidCastException("GqlCFG cannot intersect with", "GqlCFG")

        intersection = self.cfg.intersection(other.nfa)

        return GqlCFG(cfg=intersection)

    def union(self, other):
        if isinstance(other, GqlCFG):
            return GqlCFG(cfg=self.cfg.union(other.cfg))

        raise NotImplementedException("Union supported only GqlCFG types")

    def concatenate(self, other):
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
    def start(self):
        return Set(self.cfg.start_symbol.value)

    @property
    def final(self):
        raise NotImplementedException("GqlCFG final doesn't support")

    @property
    def labels(self):
        raise NotImplementedException("GqlCFG labels doesn't support")

    @property
    def edges(self):
        raise NotImplementedException("GqlCFG edges doesn't support")

    @property
    def vertices(self):
        return Set(set(self.cfg.variables))

    def get_reachable(self):
        ecfg = convert_cfg_to_ecfg(self.cfg)
        rsm = convert_ecfg_to_rsm(ecfg)
        rsm_bm = BooleanMatrices.from_rsm(rsm)
        tc = rsm_bm.make_transitive_closure()
        reachable = set()
        for i, j in zip(*tc.nonzero()):
            reachable.add((i, rsm_bm.states_to_box_variable.get((i, j)), j))

        return Set(reachable)

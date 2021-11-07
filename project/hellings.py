import networkx as nx
from pyformlang.cfg import CFG, Epsilon

from project import convert_cfg_to_wcnf

__all__ = ["hellings"]


def hellings(cfg: CFG, graph: nx.MultiDiGraph):
    wcnf = convert_cfg_to_wcnf(cfg)
    res = []
    temp = []
    for production in wcnf.productions:
        if not production.body == [Epsilon()]:
            continue
        for v in graph.nodes:
            res.append((v, production.head.value, v))
            temp.append((v, production.head.value, v))

    for u, c, v in graph.edges:
        for production in wcnf.productions:
            if len(production.body) == 0 or production.body[0].value == c:
                res.append((u, production.head.value, v))
                temp.append((u, production.head.value, v))

    while temp:
        temp_node_l, temp_variable, temp_node_r = temp.pop(0)

        for res_node_l, res_variable, res_node_r in res:
            if res_node_r != temp_node_l:
                continue

            for production in wcnf.productions:
                if len(production.body) <= 1:
                    continue
                if (
                    production.body[0].value != res_variable
                    or production.body[1].value != temp_variable
                ):
                    continue
                if (res_node_l, production.head.value, temp_node_r) in res:
                    continue

                temp.append((res_node_l, production.head.value, temp_node_r))
                res.append((res_node_l, production.head.value, temp_node_r))

        for res_node_l, res_variable, res_node_r in res:
            if res_node_l != temp_node_r:
                continue

            for production in wcnf.productions:
                if len(production.body) <= 1:
                    continue
                if (
                    production.body[0].value != temp_node_l
                    or production.body[1].value != res_variable
                ):
                    continue
                if (temp_node_l, production.head.value, res_node_r) in res:
                    continue

                temp.append((temp_node_l, production.head.value, res_node_r))
                res.append((temp_node_l, production.head.value, res_node_r))
    return res

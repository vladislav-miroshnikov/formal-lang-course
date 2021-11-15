from typing import Set, Tuple
import networkx as nx
from pyformlang.cfg import CFG, Variable
from scipy import sparse

from project import hellings, convert_cfg_to_wcnf

__all__ = ["hellings_cfpq", "matrix_cfpq"]


def hellings_cfpq(
    graph: nx.MultiDiGraph,
    cfg: CFG,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
    start_var: Variable = Variable("S"),
) -> Set[Tuple[int, int]]:
    """
    Context-Free Path Querying based on Hellings Algorithm

    Parameters
    ----------
    graph: nx.MultiDiGraph
        input graph
    cfg: CFG
        input CFG
    start_nodes: Set[int]
        set of start nodes in given graph
    final_nodes: Set[int]
        set of final nodes in given graph
    start_var: Variable
        start variable in CFG

    Returns
    -------
    Set[Tuple[int, int]]:
        set of tuples (node, node)
    """
    cfg._start_symbol = start_var
    reach_pairs = {(u, v) for u, h, v in hellings(cfg, graph) if h == cfg.start_symbol}
    if start_nodes:
        reach_pairs = {(u, v) for u, v in reach_pairs if u in start_nodes}
    if final_nodes:
        reach_pairs = {(u, v) for u, v in reach_pairs if v in final_nodes}

    return reach_pairs


def matrix_cfpq(
    graph: nx.MultiDiGraph,
    cfg: CFG,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
    start_variable: Variable = Variable("S"),
) -> Set[Tuple[int, int]]:
    """
    Context-Free Path Querying based on matrix multiplication

    Parameters
    ----------
    graph: nx.MultiDiGraph
        input graph
    cfg: CFG
        input CFG
    start_nodes: Set[int]
        set of start nodes in given graph
    final_nodes: Set[int]
        set of final nodes in given graph
    start_variable: Variable
        start variable in CFG

    Returns
    -------
    Set[Tuple[int, int]]:
        set of tuples (node, node)
    """
    cfg._start_symbol = start_variable
    wcnf = convert_cfg_to_wcnf(cfg)

    num_of_nodes = graph.number_of_nodes()
    matrices = {
        v.value: sparse.dok_matrix((num_of_nodes, num_of_nodes), dtype=bool)
        for v in wcnf.variables
    }

    term_productions = {p for p in wcnf.productions if len(p.body) == 1}
    for i, j, data in graph.edges(data=True):
        l = data["label"]
        for v in {p.head.value for p in term_productions if p.body[0].value == l}:
            matrices[v][i, j] = True

    eps_products_heads = [p.head.value for p in wcnf.productions if not p.body]
    for i in range(num_of_nodes):
        for v in eps_products_heads:
            matrices[v][i, i] = True

    changed = True
    variable_productions = {p for p in wcnf.productions if len(p.body) == 2}
    while changed:
        changed = False
        for p in variable_productions:
            old_nnz = matrices[p.head.value].nnz
            matrices[p.head.value] += (
                matrices[p.body[0].value] @ matrices[p.body[1].value]
            )
            new_nnz = matrices[p.head.value].nnz
            changed = old_nnz != new_nnz

    reach_pairs = {(u, v) for u, v in zip(*matrices[wcnf.start_symbol.value].nonzero())}
    if start_nodes:
        reach_pairs = {(u, v) for u, v in reach_pairs if u in start_nodes}
    if final_nodes:
        reach_pairs = {(u, v) for u, v in reach_pairs if v in final_nodes}

    return reach_pairs

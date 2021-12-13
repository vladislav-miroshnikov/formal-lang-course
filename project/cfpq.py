from typing import Set, Tuple
import networkx as nx
from pyformlang.cfg import CFG, Variable

from project import convert_cfg_to_wcnf
from project.cfpq_algorithms import matrix, tensor

__all__ = ["hellings_cfpq", "matrix_cfpq", "tensor_cfpq"]


def _cfpq(
    algorithm_result: Set[Tuple[int, str, int]],
    cfg: CFG,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
) -> Set[Tuple[int, int]]:
    """
    Internal function for CFPQ

    Parameters
    ----------
    algorithm_result: Set[Tuple[int, str, int]]
         result of cfpq algorithm (hellings, matrix, tensor)
    cfg: CFG
        input CFG
    start_nodes: Set[int]
        set of start nodes in given graph
    final_nodes: Set[int]
        set of final nodes in given graph

    Returns
    -------
    Set[Tuple[int, int]]:
        set of tuples (node, node)
    """
    reach_pairs = {(u, v) for u, h, v in algorithm_result if h == cfg.start_symbol}
    if start_nodes:
        reach_pairs = {(u, v) for u, v in reach_pairs if u in start_nodes}
    if final_nodes:
        reach_pairs = {(u, v) for u, v in reach_pairs if v in final_nodes}

    return reach_pairs


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

    return _cfpq(set(_hellings_alg(graph, cfg)), cfg, start_nodes, final_nodes)

def _hellings_alg(graph: nx.MultiDiGraph, cfg: CFG) -> set[Tuple[int, str, int]]:
    """
    Hellings algorithm for solving Context-Free Path Querying problem

    Parameters
    ----------
    graph: nx.MultiDiGraph
        input graph
    cfg: CFG
        input cfg

    Returns
    -------
    set[Tuple[int, str, int]]:
        set tuples (node, terminal, node)
    """
    wcnf = convert_cfg_to_wcnf(cfg)

    eps_prod_heads = [p.head.value for p in wcnf.productions if not p.body]
    term_productions = {p for p in wcnf.productions if len(p.body) == 1}
    var_productions = {p for p in wcnf.productions if len(p.body) == 2}

    r = {(v, h, v) for v in range(graph.number_of_nodes()) for h in eps_prod_heads} | {
        (u, p.head.value, v)
        for u, v, edge_data in graph.edges(data=True)
        for p in term_productions
        if p.body[0].value == edge_data["label"]
    }

    new = r.copy()
    while new:
        n, N, m = new.pop()
        r_temp = set()

        for u, M, v in r:
            if v == n:
                triplets = {
                    (u, p.head.value, m)
                    for p in var_productions
                    if p.body[0].value == M
                    and p.body[1].value == N
                    and (u, p.head.value, m) not in r
                }
                new |= triplets
                r_temp |= triplets
        r |= r_temp
        r_temp.clear()

        for u, M, v in r:
            if u == m:
                triplets = {
                    (n, p.head.value, v)
                    for p in var_productions
                    if p.body[0].value == N
                    and p.body[1].value == M
                    and (n, p.head.value, v) not in r
                }
                new |= triplets
                r_temp |= triplets
        r |= r_temp

    return r


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

    return _cfpq(set(matrix(graph, cfg)), cfg, start_nodes, final_nodes)


def tensor_cfpq(
    graph: nx.MultiDiGraph,
    cfg: CFG,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
    start_variable: Variable = Variable("S"),
) -> Set[Tuple[int, int]]:
    """
    Context-Free Path Querying based on tensor algorithm and RSM

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

    return _cfpq(set(tensor(graph, cfg)), cfg, start_nodes, final_nodes)

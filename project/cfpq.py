from typing import Set, Tuple

import networkx as nx
from pyformlang.cfg import CFG, Variable

from project import hellings, matrix, tensor

from project.cfpq_algorithms import hellings, matrix, tensor

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

    return _cfpq(set(hellings(graph, cfg)), cfg, start_nodes, final_nodes)


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

from typing import Tuple

import networkx as nx
from pyformlang.cfg import CFG
from scipy import sparse
from scipy.sparse import dok_matrix, identity

from project import (
    convert_cfg_to_wcnf,
    get_nfa_by_graph,
    BooleanMatrices,
    intersect_boolean_matrices,
)

__all__ = ["hellings", "matrix", "tensor"]


def hellings(graph: nx.MultiDiGraph, cfg: CFG) -> set[Tuple[int, str, int]]:
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


def matrix(graph: nx.MultiDiGraph, cfg: CFG) -> set[Tuple[int, str, int]]:
    """
    Matrix algorithm for solving Context-Free Path Querying problem

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
            changed = changed or old_nnz != new_nnz

    return {
        (u, variable, v)
        for variable, var_matrix in matrices.items()
        for u, v in zip(*var_matrix.nonzero())
    }


def tensor(graph: nx.MultiDiGraph, cfg: CFG) -> set[Tuple[int, str, int]]:
    """
    Tensor algorithm for solving Context-Free Path Querying problem

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

    n = sum(len(p.body) + 1 for p in wcnf.productions)
    rsm_heads = dict()
    nonterm = set()
    boxes = dict()
    start_states = set()
    final_states = set()
    counter = 0

    nfa_by_graph = get_nfa_by_graph(graph)
    bm = BooleanMatrices(nfa_by_graph)

    for p in wcnf.productions:
        nonterm.add(p.head.value)
        start_states.add(counter)
        final_states.add(counter + len(p.body))
        rsm_heads[(counter, counter + len(p.body))] = p.head.value
        for b in p.body:
            m = boxes.get(b.value, dok_matrix((n, n), dtype=bool))
            m[counter, counter + 1] = True
            boxes[b.value] = m
            counter += 1
        counter += 1

    for p in wcnf.productions:
        if len(p.body) == 0:
            bm.bool_matrices[p.head.value] = identity(
                bm.states_count, dtype=bool
            ).todok()

    changed = True
    bfa = BooleanMatrices()
    bfa.start_states = start_states
    bfa.final_states = final_states
    bfa.bool_matrices = boxes
    bfa.states_count = n

    while changed:
        changed = False
        transitive_closure = intersect_boolean_matrices(
            bfa, bm
        ).make_transitive_closure()
        x, y = transitive_closure.nonzero()

        for (i, j) in zip(x, y):
            rfa_from = i // bm.states_count
            rfa_to = j // bm.states_count
            graph_from = i % bm.states_count
            graph_to = j % bm.states_count

            if (rfa_from, rfa_to) not in rsm_heads:
                continue

            variable = rsm_heads[(rfa_from, rfa_to)]
            m = bm.bool_matrices.get(
                variable,
                dok_matrix((bm.states_count, bm.states_count), dtype=bool),
            )
            if not m[graph_from, graph_to]:
                changed = True
                m[graph_from, graph_to] = True
                bm.bool_matrices[variable] = m

    triplets = set()
    for key, m in bm.bool_matrices.items():
        if key not in nonterm:
            continue
        for (u, v), _ in m.items():
            triplets.add((u, key, v))

    return triplets

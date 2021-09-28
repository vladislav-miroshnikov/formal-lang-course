import networkx as nx

from project import get_nfa_by_graph, regex_to_min_dfa
from project.matrix import BooleanMatrices
from project.matrix_utils import intersect_boolean_matrices

__all__ = ["rpq"]


def rpq(
    graph: nx.MultiDiGraph,
    query: str,
    start_nodes: set = None,
    final_nodes: set = None,
) -> set:
    """
    Computes Regular Path Querying from given graph and regular expression

    Parameters
    ----------
    graph: MultiDiGraph
       Labeled graph
    query: str
       Regular expression given as string
    start_nodes: set, default=None
       Start states in NFA
    final_nodes: set, default=None
       Final states in NFA

    Returns
    -------
    result_set: set
       Regular Path Querying
    """
    nfa_by_graph = get_nfa_by_graph(graph, start_nodes, final_nodes)
    dfa_by_graph = regex_to_min_dfa(query)

    graph_bm = BooleanMatrices(nfa_by_graph)
    query_bm = BooleanMatrices(dfa_by_graph)

    intersected_bm = intersect_boolean_matrices(graph_bm, query_bm)
    transitive_closure = intersected_bm.make_transitive_closure()

    start_states = intersected_bm.get_start_states()
    final_states = intersected_bm.get_final_states()

    result_set = set()

    for state_from, state_to in zip(*transitive_closure.nonzero()):
        if state_from in start_states and state_to in final_states:
            result_set.add(
                (state_from // query_bm.states_count, state_to // query_bm.states_count)
            )

    return result_set

from typing import Set, Tuple

import cfpq_data
import networkx as nx

__all__ = [
    "Graph",
    "get_graph_info",
    "create_two_cycles_graph",
    "save_graph_to_dot",
    "get_nfa_by_graph",
]

from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State


class Graph:
    """
    Provides information about graph: number of nodes, number of edges, set of labels on edges.
    It has not any binding to defined graph, it simply holds a info.

    Attributes
    ----------
    nodes: int
        Count of nodes in graph
    edges: int
        Count of edges in graph
    labels: Set[str]
        Set of labels on edges
    """

    def __init__(self, nodes: int, edges: int, labels: Set[str]):
        self.nodes = nodes
        self.edges = edges
        self.labels = labels

    def __str__(self):
        return f"""
        Count of nodes: {str(self.nodes)}
        Count of edges: {str(self.edges)}
        Labels: {str(self.labels)}
    """


def get_graph_info(graph: nx.MultiDiGraph) -> Graph:
    """
    Provides information about graph by instance of Graph object

    Parameters
    ----------
    graph: nx.MultiDiGraph
        Graph from which information is gained

    Returns
    -------
    Graph
        Class with information about graph
    """
    return Graph(
        graph.number_of_nodes(),
        graph.number_of_edges(),
        cfpq_data.get_labels(graph, verbose=False),
    )


def create_two_cycles_graph(
    first_nodes_count, second_nodes_count, labels: Tuple[str, str]
) -> nx.MultiDiGraph:
    """
    Generates graph with two cycles

    Parameters
    ----------
    first_nodes_count: int
        Number of nodes in the first cycle
    second_nodes_count: int
        Number of nodes in the second cycle
    labels: Tuple[str, str]
        Labels for the edges on the first and second cycle

    Returns
    -------
    nx.MultiDiGraph
        Generated graph with two cycles
    """
    graph = cfpq_data.labeled_two_cycles_graph(
        first_nodes_count, second_nodes_count, edge_labels=labels, verbose=False
    )

    return graph


def save_graph_to_dot(graph: nx.MultiDiGraph, file_path: str) -> None:
    """
    Save graph to file with .dot extension

        Parameters
        ----------
        graph: nx.MultiDiGraph
            Graph which will be saved to file
        file_path: str
            Path to file

        Returns
        -------
        None
    """
    pydot_graph = nx.drawing.nx_pydot.to_pydot(graph)
    pydot_graph.write_raw(file_path)


def get_nfa_by_graph(
    graph: nx.MultiDiGraph, start_nodes: Set[int] = None, final_nodes: Set[int] = None
) -> NondeterministicFiniteAutomaton:
    """
    Creates a Nondeterministic Finite Automaton for a specified graph.
    If start_nodes and final_nodes are not specified, all nodes are considered start and end.
    Parameters
    ----------
    graph: nx.MultiDiGraph
        Graph for creating NFA
    start_nodes: Set[int]
        Set of start nodes
    final_nodes: Set[int]
        Set of final nodes
    Returns
    -------
    EpsilonNFA
        Epsilon Nondeterministic Finite Automaton which equivalent to graph
    Raises
    ------
    ValueError
        If node does not present in the graph
    """
    nfa = NondeterministicFiniteAutomaton()

    # add the necessary transitions to automaton
    for node_from, node_to in graph.edges():
        edge_data = graph.get_edge_data(node_from, node_to)[0]["label"]
        nfa.add_transition(node_from, edge_data, node_to)

    if (start_nodes and final_nodes) is None:
        if not nfa.states:
            for node in graph.nodes:
                nfa.add_start_state(State(node))
                nfa.add_final_state(State(node))
        else:
            for state in nfa.states:
                nfa.add_start_state(state)
                nfa.add_final_state(state)
        return nfa

    if start_nodes:
        for start_node in start_nodes:
            state = State(start_node)
            if state not in nfa.states:
                raise ValueError(f"\nNode {start_node} does not present in the graph")
            nfa.add_start_state(state)

    if final_nodes:
        for final_node in final_nodes:
            state = State(final_node)
            if state not in nfa.states:
                raise ValueError(f"\nNode {final_node} does not present in the graph")
            nfa.add_final_state(state)

    return nfa

from typing import Set, Tuple

import cfpq_data
import networkx as nx

__all__ = ["Graph", "get_graph_info", "create_two_cycles_graph", "save_graph_to_dot"]


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

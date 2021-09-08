from pathlib import Path

import cfpq_data
import networkx as nx

from project.graph_funcs import Graph, get_graph_info, create_two_cycles_graph

__all__ = ["get_graph_info_util", "create_two_cycles_graph_util", "save_to_dot"]

graph_dictionary = {}


def get_graph_info_util(graph_name) -> Graph:
    """
    Provides and prints information about graph
    Parameters
    ----------
    graph_name: str
        Name of the graph
    Returns
    -------
    Graph
        Object with information about graph
    Raises
    ------
    Exception
        If graph does not found in dataset
    """
    if all(
        graph_name not in cfpq_data.DATASET[graph_from_ds].keys()
        for graph_from_ds in cfpq_data.DATASET.keys()
    ):
        raise Exception("Graph with this name does not found in dataset.")

    graph = cfpq_data.graph_from_dataset(graph_name, verbose=False)

    graph_info = get_graph_info(graph)

    print("Information about graph:")
    print(graph_info)

    return graph_info


def create_two_cycles_graph_util(
    graph_name, first_nodes_count, second_nodes_count, first_label, second_label
) -> nx.MultiDiGraph:
    """
    Create named and labeled two cycles graph.
    Parameters
    ----------
    graph_name: str
        Name of the created graph
    first_nodes_count: str
        String representation of count of nodes on the first cycle
    second_nodes_count: str
        String representation of count of nodes on the second cycle
    first_label: str
        Label for edges in the first cycle
    second_label: str
        Label for edges in the second cycle
    Returns
    -------
    nx.MultiDiGraph
        Created graph
    """
    created_graph = create_two_cycles_graph(
        int(first_nodes_count), int(second_nodes_count), (first_label, second_label)
    )
    graph_dictionary[graph_name] = created_graph

    print(f"\nGraph {graph_name} created")
    return created_graph


def save_to_dot(graph_name, file_path) -> None:
    """
    Saves the graph to a .dot file along the given path
    Parameters
    ----------
    graph_name: str
        Name of saved graph
    file_path: str
        Path where to save graph
    Returns
    -------
    Raises
    ------
    Exception
        If graph does not found
    """
    if graph_name not in graph_dictionary:
        raise Exception(f"\nGraph with name {graph_name} does not found.")

    graph = graph_dictionary[graph_name]

    file = Path(file_path)

    if file.suffix.lower() != ".dot":
        raise Exception("\nIncorrect extension of the file path.")

    if not file.is_file():
        open(file_path, "w")

    pydot_graph = nx.drawing.nx_pydot.to_pydot(graph)
    pydot_graph.write_raw(file_path)

    print(f"\nGraph was saved by path: {file_path}")

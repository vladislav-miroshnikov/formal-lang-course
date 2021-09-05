from pathlib import Path

import cfpq_data
import networkx as nx
import pydot


def get_graph_info(graph_path):
    file = Path(graph_path)
    if not file.is_file():
        raise Exception(f"\nFile with path {graph_path} does not exist.")
    if file.suffix.lower() != ".dot":
        raise Exception("\nIncorrect extension of the file.")

    pydot_graph = pydot.graph_from_dot_file(graph_path)[0]
    graph: nx.MultiDiGraph = nx.drawing.nx_pydot.from_pydot(pydot_graph)

    print(
        f" Count of nodes: {graph.number_of_nodes()} "
        f"\n Count of edges: {graph.number_of_edges()} "
        f"\n Labels: {cfpq_data.get_labels(graph, verbose=False)}"
    )

    return {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "labels": cfpq_data.get_labels(graph),
    }


def create_graph(
    file_path, first_nodes_count, second_nodes_count, first_label, second_label
):
    path = Path(file_path)
    with open(path, "w"):
        graph = cfpq_data.labeled_two_cycles_graph(
            first_nodes_count,
            second_nodes_count,
            edge_labels=(first_label, second_label),
            verbose=False,
        )
        pydot_graph = nx.drawing.nx_pydot.to_pydot(graph)
        pydot_graph.write_raw(file_path)

    print(f"\nGraph created on the path {file_path}")

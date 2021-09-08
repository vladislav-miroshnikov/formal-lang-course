import os

import cfpq_data
import networkx as nx
from project.graph_utils import (
    create_two_cycles_graph_util,
    get_graph_info_util,
    save_to_dot,
)
from project.graph_funcs import create_two_cycles_graph


def test_get_graph_info():
    name = "wine"
    expected_graph = cfpq_data.graph_from_dataset(name, verbose=False)
    actual_graph = get_graph_info_util(name)

    assert (
        actual_graph.nodes == expected_graph.number_of_nodes()
        and actual_graph.edges == expected_graph.number_of_edges()
        and actual_graph.labels == cfpq_data.get_labels(expected_graph, verbose=False)
    )


def test_creating_and_saving_graph():
    path = "graph.dot"

    expected_graph = create_two_cycles_graph(5, 10, ("a", "b"))
    expected_graph_text = str(nx.drawing.nx_pydot.to_pydot(expected_graph))

    actual_graph = create_two_cycles_graph_util("simple_graph", "5", "10", "a", "b")
    save_to_dot("simple_graph", path)

    assert os.path.exists(path)

    with open(path, "r") as file:
        actual_graph_text = file.read()
        assert (
            actual_graph.number_of_nodes() == expected_graph.number_of_nodes()
            and actual_graph.number_of_edges() == expected_graph.number_of_edges()
            and cfpq_data.get_labels(actual_graph, verbose=False)
            == cfpq_data.get_labels(expected_graph, verbose=False)
            and actual_graph_text == expected_graph_text
        )

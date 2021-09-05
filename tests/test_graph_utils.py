import os

import cfpq_data

from project.graph_utils import create_graph, get_graph_info

path = "graph_sample.dot"


def test_graph_creation():
    create_graph(path, 5, 10, "A", "D")
    assert True == (os.path.isfile(path) and os.path.getsize(path) > 0)


def test_get_graph_info():
    test_graph_creation()
    test_graph = cfpq_data.labeled_two_cycles_graph(
        5, 10, edge_labels=("A", "D"), verbose=False
    )
    graph_info = get_graph_info(path)
    assert test_graph.number_of_nodes() == graph_info["nodes"]
    assert test_graph.number_of_edges() == graph_info["edges"]
    assert cfpq_data.get_labels(test_graph, verbose=False) == graph_info["labels"]

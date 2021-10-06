from itertools import product

import networkx as nx
import pytest

from project import create_two_cycles_graph, rpq


@pytest.fixture
def graph():
    return create_two_cycles_graph(3, 2, ("X", "Y"))


@pytest.fixture
def empty_graph():
    return nx.empty_graph(create_using=nx.MultiDiGraph)


@pytest.fixture
def acyclic_graph():
    graph = nx.MultiDiGraph()
    graph.add_edges_from(
        [(0, 1, {"label": "X"}), (1, 2, {"label": "Y"}), (2, 3, {"label": "Y"})]
    )
    return graph


@pytest.mark.parametrize(
    "query, start_nodes, final_nodes, expected_rpq",
    [
        (
            "X*|Y",
            None,
            None,
            set(product(range(4), range(4))).union({(0, 4), (4, 5), (5, 0)}),
        ),
        ("X*|Y", {0}, {1, 2, 3, 4}, {(0, 1), (0, 2), (0, 3), (0, 4)}),
        ("X*|Y", {4}, {4, 5}, {(4, 5)}),
        ("Y", {0}, {0, 1, 2, 3}, set()),
        ("Y*", {0}, {5, 4}, {(0, 5), (0, 4)}),
    ],
)
def test_rpq(graph, query, start_nodes, final_nodes, expected_rpq):
    actual_rpq = rpq(graph, query, start_nodes, final_nodes)

    assert actual_rpq == expected_rpq


def test_empty_graph(empty_graph):
    actual_rpq = rpq(empty_graph, "X|Y")
    assert actual_rpq == set()


def test_incorrect_labels_query(graph):
    actual_rpq = rpq(graph, "W|Z")
    assert actual_rpq == set()


def test_acyclic_graph(acyclic_graph):
    actual_rpq = rpq(acyclic_graph, "X Y Y")
    assert actual_rpq == {(0, 3)}


def test_empty_graph_empty_query(empty_graph):
    actual_rpq = rpq(empty_graph, "")
    assert actual_rpq == set()

from itertools import product

import pytest

from project import create_two_cycles_graph, rpq


@pytest.fixture
def graph():
    return create_two_cycles_graph(3, 2, ("X", "Y"))


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

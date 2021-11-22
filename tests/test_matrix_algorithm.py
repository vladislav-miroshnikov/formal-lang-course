import pytest
from cfpq_data import labeled_cycle_graph
from pyformlang.cfg import CFG

from project import create_two_cycles_graph
from project.cfpq_algorithms import matrix


@pytest.mark.parametrize(
    "cfg, graph, exp_ans",
    [
        (
            """
                S -> epsilon
                """,
            labeled_cycle_graph(5, "a"),
            {(0, "S", 0), (1, "S", 1), (2, "S", 2), (3, "S", 3), (4, "S", 4)},
        ),
        (
            """
                    S -> a | epsilon
                    """,
            labeled_cycle_graph(3, "a"),
            {
                (0, "S", 0),
                (1, "S", 1),
                (2, "S", 2),
                (0, "S", 1),
                (1, "S", 2),
                (2, "S", 0),
            },
        ),
        (
            """
                    S -> A B
                    S -> A C
                    C -> S B
                    A -> a
                    B -> b
                """,
            create_two_cycles_graph(3, 2, ("a", "b")),
            {
                (0, "A", 1),
                (1, "A", 2),
                (2, "A", 3),
                (3, "A", 0),
                (0, "B", 4),
                (4, "B", 5),
                (5, "B", 0),
                (3, "S", 4),
                (2, "S", 5),
                (1, "S", 0),
                (0, "S", 4),
                (3, "S", 5),
                (2, "S", 0),
                (1, "S", 4),
                (0, "S", 5),
                (3, "S", 0),
                (2, "S", 4),
                (1, "S", 5),
                (0, "S", 0),
                (3, "C", 5),
                (2, "C", 0),
                (1, "C", 4),
                (0, "C", 5),
                (3, "C", 0),
                (2, "C", 4),
                (1, "C", 5),
                (0, "C", 0),
                (3, "C", 4),
                (2, "C", 5),
                (1, "C", 0),
                (0, "C", 4),
            },
        ),
    ],
)
def test_matrix(cfg, graph, exp_ans):
    assert matrix(graph, CFG.from_text(cfg)) == exp_ans

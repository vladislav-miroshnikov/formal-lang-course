import os

import cfpq_data
import networkx as nx
import pytest
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State

from project.graph_utils import (
    create_two_cycles_graph_util,
    get_graph_info_util,
    save_to_dot,
)
from project.graph_funcs import create_two_cycles_graph, get_nfa_by_graph


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


@pytest.fixture
def two_cycles_graph() -> nx.MultiDiGraph:
    return create_two_cycles_graph(2, 2, ("X", "Y"))


def test_check_is_nfa(two_cycles_graph):
    nfa = get_nfa_by_graph(two_cycles_graph)
    assert not nfa.is_deterministic()


@pytest.mark.parametrize(
    "start_states, final_states",
    [
        ({30, 40}, {20, 10}),
        ({-100, 1}, {0, 1000}),
    ],
)
def test_wrong_node_in_nfa(two_cycles_graph, start_states, final_states):
    with pytest.raises(ValueError):
        get_nfa_by_graph(two_cycles_graph, start_states, final_states)


@pytest.mark.parametrize(
    "start_states, final_states",
    [
        (None, None),
        ({0, 1}, {1, 2}),
        ({0, 1, 2}, {3, 4}),
        (None, {4}),
        ({2, 3, 4}, None),
    ],
)
def test_nfa_is_equivalent(two_cycles_graph, start_states, final_states):
    expected_nfa = NondeterministicFiniteAutomaton()
    expected_nfa.add_transitions(
        [(0, "X", 1), (1, "X", 2), (2, "X", 0), (0, "Y", 3), (3, "Y", 4), (4, "Y", 0)]
    )

    if not start_states:
        start_states = {0, 1, 2, 3, 4}
    if not final_states:
        final_states = {0, 1, 2, 3, 4}

    for state in start_states:
        expected_nfa.add_start_state(State(state))
    for state in final_states:
        expected_nfa.add_final_state(State(state))

    actual_nfa = get_nfa_by_graph(two_cycles_graph, start_states, final_states)
    assert actual_nfa.is_equivalent_to(expected_nfa)


@pytest.mark.parametrize(
    "accepting_words, not_accepting_words",
    [(["", "XXX", "XXXYYY", "YYYX"], ["epsilon", "XYXYXY", "XXYY", "XXYXYXY"])],
)
def test_nfa_accepting_words(two_cycles_graph, accepting_words, not_accepting_words):
    nfa = get_nfa_by_graph(two_cycles_graph)
    assert all(nfa.accepts(word) for word in accepting_words) and not all(
        nfa.accepts(word) for word in not_accepting_words
    )

from project.graph_query_language.interpreter.gql_exceptions import LoadGraphException
from project.graph_query_language.interpreter.gql_types.finite_automata import (
    FiniteAutomata,
)
from project.graph_utils import get_graph


def get_graph_by_name(name: str) -> FiniteAutomata:
    try:
        graph = get_graph(name)
    except Exception as exc:
        raise LoadGraphException(name=name) from exc

    return FiniteAutomata.fromGraph(graph)

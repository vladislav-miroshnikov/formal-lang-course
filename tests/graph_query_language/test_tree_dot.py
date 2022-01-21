import os

from project.graph_query_language.parser import write_to_dot

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
expected_graph_path = os.sep.join(
    [root_path, "graph_query_language", "data", "expected_graph.dot"]
)
actual_graph_path = os.sep.join(
    [root_path, "graph_query_language", "data", "actual_graph.dot"]
)


def test_write_to_dot():
    line = """Ig1 = load graph 'wine'
Ig1 = load graph from 'home/wine.dot'
Iquery1 = ('type' || Il1)**\n"""
    status = write_to_dot(line, actual_graph_path)
    obtained = open(actual_graph_path, "r")

    expected = open(expected_graph_path, "r")
    assert (expected.read() == obtained.read()) and status


def test_incorrect_text():
    line = """Ig1 let = load graph 'wine'
Ig1 = load graph from 'home/wine.dot'
Iquery1 = ('type' || Il1)**\n"""
    status = write_to_dot(line, actual_graph_path)

    assert status == False

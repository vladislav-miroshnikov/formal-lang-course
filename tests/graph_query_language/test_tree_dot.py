import sys

import pytest
import os

from project.dot_generator import generate_dot

from antlr4.error.Errors import ParseCancellationException


def test_write_dot(tmpdir):
    text = """g = load "go";
g = set start of (set final of g to (select vertices from g)) to {1..100};
l1 = "l1" | "l2";
q1 = ("type" | l1)*;
q2 = "subclass_of" . q;
res1 = g & q1;
res2 = g & q2;
s = select start vertices from g;
vertices1 = filter (fun v: v in s) (map (fun ((u_g,u_q1),l,(v_g,v_q1)): u_g) (select edges from res1));
vertices2 = filter (fun v: v in s) (map (fun ((u_g,u_q2),l,(v_g,v_q1)): u_g) (select edges from res2));
vertices3 = vertices1 & vertices2;
print vertices3;
"""
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    expected_graph_path = os.sep.join(
        [root_path, "graph_query_language", "expected_graph.dot"]
    )
    actual_graph_path = os.sep.join(
        [root_path, "graph_query_language", "actual_graph.dot"]
    )

    generate_dot(text, actual_graph_path)

    with open(expected_graph_path, "r") as file1:
        with open(actual_graph_path, "r") as file2:
            assert file1.read() == file2.read()


def test_incorrect_text():
    text = """g = load graph "skos";
common_labels = (select lables from g) & (select labels from (load graph "graph.txt"));
print common_labels;"""
    with pytest.raises(ParseCancellationException):
        generate_dot(text, "test")

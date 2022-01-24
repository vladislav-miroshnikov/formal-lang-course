import sys

import pytest

from project.graph_query_language.parser import parse


@pytest.mark.parametrize(
    "text, accept",
    [
        (
            """
g = load "go";
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
""",
            True,
        ),
        ('g = load "go"', False),
    ],
)
def test_parse_prog(text, accept):
    parser = parse(text)
    parser.removeErrorListeners()
    _ = parser.prog()
    act = parser.getNumberOfSyntaxErrors() == 0
    assert act == accept


@pytest.mark.parametrize(
    "text, accept",
    [
        ("print g2", True),
        ("prnt g2", False),
        ("print {1..100}", True),
        ("print", False),
        ('g1 = load "wine" ', True),
        ("g1 = load", False),
        ("g1 = {1..100}", True),
    ],
)
def test_parse_statement(text, accept):
    parser = parse(text)
    parser.removeErrorListeners()
    _ = parser.stmt()
    act = parser.getNumberOfSyntaxErrors() == 0
    assert act == accept


@pytest.mark.parametrize(
    "text, accept",
    [
        ("g1 & g2", True),
        ("g1", True),
        ("{2..100} & {1}", True),
        ("", False),
        ("(select edges from g) & {(1, 2)}", True),
        ("(select from g) & {(1, 2)}", False),
        ("l1 . l2 . l3 | l4", True),
        ("l1 . l2 . l3 & l4", True),
        ('"label1" . "label2" | "label3"', True),
        ("filter (fun (x, y): x in s) g", True),
    ],
)
def test_parse_expr(text, accept):
    parser = parse(text)
    parser.removeErrorListeners()
    _ = parser.expr()
    act = parser.getNumberOfSyntaxErrors() == 0
    assert act == accept


@pytest.mark.parametrize(
    "text, accept",
    [
        ("_a", True),
        ("graph1", True),
        ("213", False),
        ("неверный ввод", False),
    ],
)
def test_parse_variable(text, accept):
    parser = parse(text)
    parser.removeErrorListeners()
    _ = parser.var()
    act = parser.getNumberOfSyntaxErrors() == 0
    assert act == accept


@pytest.mark.parametrize(
    "text, accept",
    [
        ("fun x, y, z : x", True),
        ("fun v: v in s", True),
        ("fun ((u_g,u_q2),l,(v_g,v_q1)) : u_g", True),
        ("fun {x, y, z} : 1", False),
        ("fun 1, 2, 3: 1", False),
        ("fun x,y,z-> x", False),
    ],
)
def test_parse_lambda(text, accept):
    parser = parse(text)
    parser.removeErrorListeners()
    _ = parser.anfunc()
    act = parser.getNumberOfSyntaxErrors() == 0
    assert act == accept


@pytest.mark.parametrize(
    "text, accept",
    [
        ("map (fun x : x) g", True),
        ("map (fun ((u_g,u_q1),l,(v_g,v_q1)): u_g) (select edges from res1)", True),
        (" map (fun 1 : 1) 1", False),
        ("map p p", False),
    ],
)
def test_parse_map(text, accept):
    parser = parse(text)
    parser.removeErrorListeners()
    _ = parser.mapping()
    act = parser.getNumberOfSyntaxErrors() == 0
    assert act == accept


@pytest.mark.parametrize(
    "text, accept",
    [
        ("filter (fun x: x) g", True),
        (
            "filter (fun ((u_g,u_q1),l,(v_g,v_q1)): u_g) (select edges from res1)",
            True,
        ),
        (" filter (fun 1: 1) 1", False),
        ("filter p p", False),
    ],
)
def test_parse_filter(text, accept):
    parser = parse(text)
    parser.removeErrorListeners()
    _ = parser.filtering()
    act = parser.getNumberOfSyntaxErrors() == 0
    assert act == accept


@pytest.mark.parametrize(
    "text, accept",
    [
        ("true", True),
        ("false", True),
        ("True", False),
        ("False", False),
        ("{1..100}", True),
        ("(1..100)", False),
        ("{1, 2, 3}", True),
        ("{1, 2, 3)", False),
        (
            '''"""
    S -> A S B S
    A -> a
    B -> b
    """
    ''',
            True,
        ),
        ('(1, "l", 2)', True),
        ('("l", "k", "m")', False),
        ("{(1, 2), (3, 4), (5, 6)}", True),
        ("{(1, 2), ('l', 4), (5, 6)}", False),
        ('"label"', True),
        ("label", False),
        ('{"l1", "l2"}', True),
        ('{"l1", l2}', False),
        ("0", True),
        ("_0", False),
        ("set start of g to {1..100}", True),
        ("set start of g to {1,,100}", False),
        ("set final of g to {1..100}", True),
        ("add start of g to {1, 2, 3}", True),
        ("add final of g to labels1", True),
        ("select vertices from g", True),
        ("select start vertices from g", True),
        ("select reachable vertices from g", True),
        ("select from g", False),
        ("select labels from g", True),
        ("select edges from g", True),
        ("select edges from 1", False),
        ("select start from 1", False),
    ],
)
def test_parse_val(text, accept):
    parser = parse(text)
    parser.removeErrorListeners()
    _ = parser.val()
    act = parser.getNumberOfSyntaxErrors() == 0
    assert act == accept

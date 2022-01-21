from project.graph_query_language.parser import *


def test_load_text():
    s = parse_to_string("Ig1 = load graph 'wine'\n")
    assert (
        s == "(prog (stm (var Ig1) = (expr (load load graph (path 'wine')))) \\n <EOF>)"
    )


def test_load_from_text():
    s = parse_to_string("Ig1 = load graph from 'home/wine.dot'\n")
    assert (
        s
        == "(prog (stm (var Ig1) = (expr (load load graph from (path 'home/wine.dot')))) \\n <EOF>)"
    )


def test_and_or_star_text():
    s = parse_to_string("Iquery1 = Il0 && ('type' || Il1)**\n")
    assert (
        s
        == "(prog (stm (var Iquery1) = (expr (expr (var Il0)) (intersect &&) (expr (star ( (expr (expr (val 'type')) (union ||) (expr (var Il1))) )**)))) \\n <EOF>)"
    )


def test_load_accept():
    s = is_in_grammar("Ig1 = load graph 'wine'\n")
    assert s == True


def test_load_from_accept():
    s = is_in_grammar("Ig1 = load graph from 'home/wine.dot'\n")
    assert s == True


def test_and_or_star_accept():
    s = is_in_grammar("Iquery1 = Il0 && ('type' || Il1)**\n")
    assert s == True


def test_and_or_star_fail():
    s = is_in_grammar("as Ig1 = load graph 'wine'\n")
    assert s == False

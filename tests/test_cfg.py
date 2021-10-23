import os

import pytest
from pyformlang.cfg import CFG, Variable, Production, Epsilon, Terminal

from project.cfg import process_wcnf_from_file, is_weak_normal_form


def test_wrong_file():
    path_not_exists = "tests/data/cfg/emp"
    path_not_txt = "tests/data/cfg/empty"
    path_to_empty = "tests/data/cfg/empty.txt"

    with pytest.raises(OSError):
        process_wcnf_from_file(path_not_exists)
    with pytest.raises(OSError):
        process_wcnf_from_file(path_not_txt)
    with pytest.raises(OSError):
        process_wcnf_from_file(path_to_empty)


def test_wrong_text():
    with pytest.raises(ValueError):
        process_wcnf_from_file("tests/data/cfg/incorrect_grammar.txt")


@pytest.fixture
def read_csg() -> CFG:
    def _method(path: str, start_symbol: str = None) -> CFG:
        if not os.path.exists(path):
            print(path)
            raise OSError("Incorrect file path specified: file is not exists")
        if not path.endswith(".txt"):
            raise OSError("Incorrect file path specified: *.txt is required")
        if os.path.getsize(path) == 0:
            raise OSError("Incorrect file path specified: file is empty")

        with open(path, "r") as file:
            cfg_str = file.read()

        cfg = CFG.from_text(cfg_str, Variable(start_symbol))
        return cfg

    return _method


@pytest.mark.parametrize(
    "filename, axiom",
    [("epsilon.txt", "E"), ("grammar.txt", "S"), ("random.txt", "S")],
)
def test_process_wcnf_from_file(read_csg, filename, axiom):
    path = "tests/data/cfg/" + filename

    csg = read_csg(path, axiom)
    wcnf = process_wcnf_from_file(path, axiom)

    assert is_weak_normal_form(csg, wcnf)


@pytest.mark.parametrize(
    "filename, axiom",
    [("epsilon.txt", "E"), ("grammar.txt", "S"), ("random.txt", "Hello")],
)
def test_cnf_from_file_start_symbol(filename, axiom):
    path = "tests/data/cfg/" + filename

    wcnf = process_wcnf_from_file(path, axiom)

    assert wcnf.start_symbol == Variable(axiom)


@pytest.mark.parametrize(
    "filename, axiom, productions",
    [
        ("epsilon.txt", "E", {Production(Variable("E"), [Epsilon()])}),
        (
            "grammar.txt",
            "S",
            {
                Production(Variable("C#CNF#1"), [Variable("S"), Variable("b#CNF#")]),
                Production(Variable("S"), [Variable("a#CNF#"), Variable("C#CNF#1")]),
                Production(Variable("S"), [Variable("S"), Variable("S")]),
                Production(Variable("b#CNF#"), [Terminal("b")]),
                Production(Variable("S"), []),
                Production(Variable("a#CNF#"), [Terminal("a")]),
            },
        ),
        (
            "random.txt",
            "S",
            {
                Production(Variable("a#CNF#"), [Terminal("a")]),
                Production(Variable("S"), [Variable("a#CNF#"), Variable("C#CNF#1")]),
                Production(Variable("b#CNF#"), [Terminal("b")]),
                Production(Variable("c#CNF#"), [Terminal("c")]),
                Production(
                    Variable("C#CNF#1"), [Variable("b#CNF#"), Variable("c#CNF#")]
                ),
            },
        ),
    ],
)
def test_cnf_from_file_productions(filename, axiom, productions):
    path = "tests/data/cfg/" + filename
    wcnf = process_wcnf_from_file(path, axiom)
    assert set(wcnf.productions) == set(productions)

import pytest
from pyformlang.cfg import Variable, CFG
from pyformlang.regular_expression import Regex

from project import (
    read_ecfg_from_text,
    regex_to_min_dfa,
    read_ecfg_from_file,
    convert_cfg_to_ecfg,
)


@pytest.mark.parametrize(
    "text_cfg",
    [
        """S -> A -> B""",
        """A -> b B -> a""",
        """
        S -> a S b S
        A -> B ->
        """,
    ],
)
def test_more_one_production_on_line(text_cfg):
    with pytest.raises(Exception):
        read_ecfg_from_text(text_cfg)


@pytest.mark.parametrize(
    "text_cfg",
    [
        """
        S -> A
        S -> B
        """,
        """
        A -> b
        b -> A
        A -> c""",
    ],
)
def test_more_one_production_for_variable(text_cfg):
    with pytest.raises(Exception):
        read_ecfg_from_text(text_cfg)


@pytest.fixture
def verify_regex() -> bool:
    # Python convention for 'internal' symbols
    # See https://docs.python.org/2/tutorial/classes.html#private-variables-and-class-local-references
    def _method(r1: Regex, r2: Regex) -> bool:
        return regex_to_min_dfa(str(r1)).is_equivalent_to(regex_to_min_dfa(str(r2)))

    return _method


@pytest.mark.parametrize(
    "text_ecfg, expected_productions",
    [
        ("""""", []),
        ("""S -> epsilon""", {Variable("S"): Regex("epsilon")}),
        (
            """S -> a S b S""",
            {
                Variable("S"): Regex("a S b S"),
            },
        ),
        (
            """
                 S -> (a (S | c) b)* | S S
                 A -> a c
                 a -> b
                """,
            {
                Variable("S"): Regex("(a (S | c) b)* | S S"),
                Variable("A"): Regex("a c"),
                Variable("a"): Regex("b"),
            },
        ),
        ("""S -> (a | b)* c""", {Variable("S"): Regex("(a | b)* c")}),
    ],
)
def test_read_from_text(verify_regex, text_ecfg, expected_productions):
    ecfg = read_ecfg_from_text(text_ecfg)
    assert len(ecfg.productions) == len(expected_productions) and all(
        verify_regex(product.body, expected_productions[product.head])
        for product in ecfg.productions
    )


@pytest.mark.parametrize(
    "filename, expected_productions",
    [
        ("empty.txt", []),
        ("epsilon.txt", {Variable("S"): Regex("epsilon")}),
        (
            "grammar.txt",
            {
                Variable("S"): Regex("(a (S | c) b)* | S S"),
                Variable("A"): Regex("a c"),
                Variable("a"): Regex("b"),
            },
        ),
    ],
)
def test_read_from_file(verify_regex, filename, expected_productions):
    path = "tests/data/ecfg/" + filename
    ecfg_from_file = read_ecfg_from_file(path=path)
    assert len(ecfg_from_file.productions) == len(expected_productions) and all(
        verify_regex(product.body, expected_productions[product.head])
        for product in ecfg_from_file.productions
    )


@pytest.mark.parametrize(
    "cfg, expected_ecfg_productions",
    [
        (
            """
                    S -> epsilon
                    """,
            {Variable("S"): Regex("$")},
        ),
        (
            """
                 S -> a S | c b | S S
                 A -> a c
                 a -> b
                """,
            {
                Variable("S"): Regex("a S | c b | S S"),
                Variable("A"): Regex("a c"),
                Variable("a"): Regex("b"),
            },
        ),
        ("""S -> a | b c""", {Variable("S"): Regex("a | b c")}),
    ],
)
def test_ecfg_productions(cfg, expected_ecfg_productions):
    ecfg = convert_cfg_to_ecfg(CFG.from_text(cfg))
    ecfg_productions = ecfg.productions
    assert all(
        regex_to_min_dfa(str(p.body)).is_equivalent_to(
            regex_to_min_dfa(str(expected_ecfg_productions[p.head]))
        )
        for p in ecfg_productions
    ) and len(ecfg_productions) == len(expected_ecfg_productions)

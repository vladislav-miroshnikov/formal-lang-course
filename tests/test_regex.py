from project.regex import regex_to_dfa
from pyformlang.finite_automaton import Symbol

regex_str = "01(2)* 3*"


def test_regex_to_dfa_is_deterministic():
    dfa = regex_to_dfa(regex_str)
    assert dfa.is_deterministic()


def test_regex_to_dfa_accepting_words():
    dfa = regex_to_dfa(regex_str)

    accepting_words = [
        [Symbol("01")],
        [Symbol("01"), Symbol("3")],
        [Symbol("01"), Symbol("3")],
        [Symbol("01"), Symbol("2"), Symbol("3")],
        [Symbol("01"), Symbol("2"), Symbol("2"), Symbol("3"), Symbol("3")],
    ]

    not_accepting_words = [[], [Symbol("2"), Symbol("3")], [Symbol("1"), Symbol("3")]]

    assert all(dfa.accepts(word) for word in accepting_words) and not all(
        dfa.accepts(word) for word in not_accepting_words
    )

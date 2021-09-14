import pytest
from pyformlang.regular_expression import MisformedRegexError

from project.regex import regex_to_min_dfa
from pyformlang.finite_automaton import Symbol, State, DeterministicFiniteAutomaton

regex_str = "01(2)* 3*"


def test_regex_to_dfa_is_deterministic() -> None:
    dfa = regex_to_min_dfa(regex_str)
    assert dfa.is_deterministic()


def test_incorrect_regex():
    with pytest.raises(MisformedRegexError):
        regex_to_min_dfa("----|*incorrect****|||+++")


def test_creating_min_dfa() -> None:
    expected_dfa = DeterministicFiniteAutomaton()

    state_0 = State(0)
    state_1 = State(1)
    state_2 = State(2)

    symbol_0 = Symbol("0")
    symbol_1 = Symbol("1")
    symbol_2 = Symbol("2")

    expected_dfa.add_start_state(state_0)
    expected_dfa.add_final_state(state_0)
    expected_dfa.add_final_state(state_1)
    expected_dfa.add_final_state(state_2)

    expected_dfa.add_transition(state_0, symbol_0, state_0)
    expected_dfa.add_transition(state_0, symbol_1, state_1)
    expected_dfa.add_transition(state_0, symbol_2, state_2)

    expected_dfa.add_transition(state_1, symbol_1, state_1)
    expected_dfa.add_transition(state_1, symbol_2, state_2)

    expected_dfa.add_transition(state_2, symbol_2, state_2)

    actual_dfa = regex_to_min_dfa("0* 1* 2*")

    assert expected_dfa.is_equivalent_to(actual_dfa) and len(actual_dfa.states) == len(
        expected_dfa.states
    )


@pytest.mark.parametrize(
    "regular_expression, accepting_words, not_accepting_words",
    [
        ("", [], [[Symbol("1")], [Symbol("22"), Symbol("abc")]]),
        (
            "01(2)* 3*",
            [
                [Symbol("01")],
                [Symbol("01"), Symbol("3")],
                [Symbol("01"), Symbol("3")],
                [Symbol("01"), Symbol("2"), Symbol("3")],
                [Symbol("01"), Symbol("2"), Symbol("2"), Symbol("3"), Symbol("3")],
            ],
            [[], [Symbol("2"), Symbol("3")], [Symbol("1"), Symbol("3")]],
        ),
        (
            "vlad@(yahoo|hotmail|gmail)\.com",
            [[Symbol("vlad@"), Symbol("gmail"), Symbol(".com")]],
            [[Symbol("vlad@"), Symbol("yandex"), Symbol(".ru")]],
        ),
    ],
)
def test_regex_to_dfa_accepting_words(
    regular_expression, accepting_words, not_accepting_words
) -> None:
    dfa = regex_to_min_dfa(regular_expression)

    assert all(dfa.accepts(word) for word in accepting_words) and not all(
        dfa.accepts(word) for word in not_accepting_words
    )

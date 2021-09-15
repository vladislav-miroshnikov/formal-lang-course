from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.regular_expression import Regex

__all__ = ["regex_to_min_dfa"]


def regex_to_min_dfa(regex_str: str) -> DeterministicFiniteAutomaton:
    """
    Generates deterministic automata by regular expression

    Parameters
    ----------
    regex_str: str
        String representation of regular expression

    Returns
    -------
    DeterministicFiniteAutomaton
        Generated deterministic automata

    Raises
    ------
    MisformedRegexError
    If the regular expression is misformed.
    """
    regex = Regex(regex_str)
    enfa = regex.to_epsilon_nfa()
    dfa = enfa.to_deterministic()
    min_dfa = dfa.minimize()
    return min_dfa

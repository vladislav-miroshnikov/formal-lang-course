from pyformlang.regular_expression import MisformedRegexError

from project.graph_query_language.interpreter.gql_exceptions import InvalidCastException
from project.graph_query_language.interpreter.gql_types.base_type import BaseType
from project.graph_query_language.interpreter.gql_types.finite_automata import (
    FiniteAutomata,
)
from project.regex import regex_to_min_dfa


class Regex(BaseType):
    def __init__(self, regex_str: str):
        self.regex_str = regex_str

    @classmethod
    def fromString(cls, regex_str: str):
        try:
            return FiniteAutomata(nfa=regex_to_min_dfa(regex_str))
        except MisformedRegexError as exc:
            raise InvalidCastException(lhs="str", rhs="Regex") from exc

    def __str__(self):
        return self.regex_str.lstrip("(").rstrip(")")

    def intersect(self, other):
        lhs = Regex.fromString(self.regex_str)
        if isinstance(other, Regex):
            rhs = Regex.fromString(other.regex_str)
            return lhs.intersect(rhs)
        elif isinstance(other, FiniteAutomata):
            return lhs.intersect(other)
        else:
            raise InvalidCastException(lhs="Regex", rhs=str(other))

    def concatenate(self, other):
        return Regex(regex_str=f"({self.regex_str}.{other.regex_str})")

    def union(self, other):
        return Regex(regex_str=f"({self.regex_str}|{other.regex_str})")

    def inverse(self):
        nfa = Regex.fromString(self.regex_str)
        return nfa.inverse()

    def kleene(self):
        return Regex(regex_str=f"({self.regex_str})*")

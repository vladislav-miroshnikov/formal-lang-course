from typing import AbstractSet, Iterable

from pyformlang.cfg import Variable
from pyformlang.regular_expression import Regex

__all__ = ["ECFG", "ExtendedProduction"]


class ExtendedProduction:
    """
    This class represents ECFG production.

    Attributes
    ----------
    head: variable
        production manager
    body: Regex
        the body of the production, represented by a regular expression
    """

    def __init__(self, head: Variable, body: Regex):
        self._head = head
        self._body = body

    def __str__(self):
        return str(self.head) + " -> " + str(self.body)

    @property
    def head(self) -> Variable:
        return self._head

    @property
    def body(self) -> Regex:
        return self._body


class ECFG:
    """
    This class represents an extended CFG.
    Extended CFG:
        - There is exactly one rule for each nonterminal.
        - One line contains exactly one rule.
        - Rule non-terminal and regex for terminals and non-terminals accepted by pyformlang, separated by '->' sign.
          For example: S -> X * | Y *

    Attributes
    ----------
    variables: AbstractSet [Variable]
        ECFG Variable Set
    start_symbol: variable
        ECFG start character
    productions: Iterable [_ExtendedProduction]
        Collection containing ECFG works
    """

    def __init__(
        self,
        start_symbol: Variable = None,
        variables: AbstractSet[Variable] = None,
        productions: Iterable[ExtendedProduction] = None,
    ):
        self._start_symbol = start_symbol
        self._variables = variables or set()
        self._productions = productions or set()

    @property
    def start_symbol(self) -> Variable:
        return self._start_symbol

    @property
    def variables(self) -> AbstractSet[Variable]:
        return self._variables

    @property
    def productions(self) -> AbstractSet[ExtendedProduction]:
        return self._productions

    def to_simple_text(self) -> str:
        """
        Get a string representation of ECFG

        Returns
        -------
        str:
            String representation of ECFG
        """
        return "\n".join(str(p) for p in self.productions)

from typing import Iterable

from pyformlang.cfg import Variable
from pyformlang.finite_automaton import DeterministicFiniteAutomaton

__all__ = ["Box", "RSM"]


class Box:
    """
    Represents a box for recursive state machine

    Attributes
    ----------
    variable : Variable
       variable of RSM
    dfa : DeterministicFiniteAutomaton
        Deterministic Finite Automaton for variable
    """

    def __init__(
        self, variable: Variable = None, dfa: DeterministicFiniteAutomaton = None
    ):
        self._variable = variable
        self._dfa = dfa

    def __eq__(self, other: "Box"):
        return self._variable == other._variable and self._dfa.is_equivalent_to(
            other._dfa
        )

    @property
    def variable(self):
        return self._variable

    @property
    def dfa(self):
        return self._dfa

    def minimize(self) -> None:
        """
        Minimize dfa

        Returns
        -------
            None
        """
        self._dfa = self._dfa.minimize()


class RSM:
    """
    Represents a recursive state machine (RSM).

    Attributes
    ----------
    start_symbol : Variable
        A start symbol for automaton
    boxes : Iterable[Box]
        A finite collection of boxes
    """

    def __init__(
        self,
        start_symbol: Variable,
        boxes: Iterable[Box],
    ):
        self._start_symbol = start_symbol
        self._boxes = boxes

    @property
    def start_symbol(self):
        return self._start_symbol

    @property
    def boxes(self):
        return self._boxes

    def set_start_symbol(self, start_symbol: Variable):
        self._start_symbol = start_symbol

    def minimize(self):
        """
        Minimize dfa for each box in boxes

        Returns
        -------
            rsm: Minimized RSM
        """
        for box in self._boxes:
            box.minimize()
        return self

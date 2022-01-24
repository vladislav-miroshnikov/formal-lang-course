from project.graph_query_language.interpreter.gql_exceptions import (
    NotImplementedException,
)
from project.graph_query_language.interpreter.gql_types.base_type import BaseType


class Bool(BaseType):
    """
    GQL boolean type

    Attributes
    ----------
    b: bool
        Internal boolean value
    """

    def __init__(self, b: bool):
        self.b = b

    def __bool__(self):
        return self.b

    def __hash__(self):
        return hash(self.b)

    def __str__(self):
        return "true" if self.b else "false"

    def __eq__(self, other: "Bool") -> bool:
        return self.b == other.b

    def intersect(self, other: "Bool") -> "Bool":
        """
        '&' (AND) operation

        Parameters
        ----------
        other: Bool
            Boolean object

        Returns
        -------
        intersection: Bool
            Logical 'AND'
        """
        return Bool(self.b and other.b)

    def union(self, other: "Bool") -> "Bool":
        """
        | (OR) operation

        Parameters
        ----------
        other: Bool
            Boolean object

        Returns
        -------
        intersection: Bool
            Logical 'OR'
        """
        return Bool(self.b or other.b)

    def concatenate(self, other: "Bool"):
        raise NotImplementedException("Bool doesn't support '.' operation")

    def inverse(self) -> "Bool":
        """
        not (NOT) operation

        Returns
        -------
        complement: Bool
            Logical 'NOT'
        """
        return Bool(not self.b)

    def kleene(self):
        raise NotImplementedException("Bool doesn't support '*' operation")

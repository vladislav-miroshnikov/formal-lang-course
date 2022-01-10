from project.graph_query_language.interpreter.gql_exceptions import (
    NotImplementedException,
)
from project.graph_query_language.interpreter.gql_types.base_type import BaseType


class Bool(BaseType):
    def __init__(self, b: bool):
        self.b = b

    def __bool__(self):
        return self.b

    def __str__(self):
        return "true" if self.b else "false"

    def intersect(self, other: "Bool") -> "Bool":
        return Bool(self.b and other.b)

    def union(self, other: "Bool") -> "Bool":
        return Bool(self.b or other.b)

    def concatenate(self, other: "Bool"):
        raise NotImplementedException("Bool doesn't support '.' operation")

    def inverse(self):
        return Bool(not self.b)

    def kleene(self):
        raise NotImplementedException("Bool doesn't support '*' operation")

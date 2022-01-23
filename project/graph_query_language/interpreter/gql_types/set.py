from project.graph_query_language.interpreter.gql_exceptions import (
    NotImplementedException,
    GQLTypeError,
)
from project.graph_query_language.interpreter.gql_types.base_type import BaseType
from project.graph_query_language.interpreter.gql_types.bool import Bool


class Set(BaseType):
    """
    GQL Set object

    Attributes
    ----------
    internal_set: set
        Python set object
    """

    def __init__(self, internal_set: set):
        self._type = Set.get_type(internal_set)
        self._set = internal_set

    def __str__(self):
        return "{" + ", ".join(map(lambda x: str(x), self.data)) + "}"

    @staticmethod
    def get_type(set_obj: set) -> type:
        """
        Parameters
        ----------
        set_obj: set
            Python set object

        Returns
        -------
        t: type
            First element type
        """
        if len(set_obj) == 0:
            return type(None)
        iseq = iter(set_obj)
        return type(next(iseq))

    @staticmethod
    def _check_type_consistency(set_obj: set) -> bool:
        """
        Parameters
        ----------
        set_obj: set
            Python set object

        Returns
        -------
        is_consistent: bool
            True if elements have one type, False otherwise
        """
        if len(set_obj) == 0:
            return True
        iseq = iter(set_obj)
        t = type(next(iseq))
        return all(map(lambda x: isinstance(x, t), iseq))

    @classmethod
    def fromSet(cls, pyset: set) -> "Set":
        """
        Parameters
        ----------
        pyset: set
            Python set object

        Returns
        -------
        set: Set
            Ser object

        Raises
        ------
        GQLTypeError
            If set type is inconsistent
        """
        if not Set._check_type_consistency(pyset):
            raise GQLTypeError("Type consistency failed")
        return Set(pyset)

    @property
    def set_type(self) -> type:
        return self._type

    @property
    def data(self) -> set:
        return self._set

    def __len__(self):
        return len(self._set)

    def find(self, value) -> Bool:
        """
        Check whether value in set or not

        Parameters
        ----------
        value
            searchable object

        Returns
        -------
        b: Bool
            True if value is in internal set, False otherwise
        """
        return Bool(value in self._set)

    def intersect(self, other: "Set") -> "Set":
        """
        Intersection of two sets

        Parameters
        ----------
        other: Set
            Another set object to intersect

        Returns
        -------
        intersection: Set
            Intersection of two sets

        Raises
        ------
        GQLTypeError
            If given sets have different types
        """
        if self.data and other.data and self.set_type != other.set_type:
            raise GQLTypeError(f"Types mismatched: {self.set_type} != {other.set_type}")
        return Set(internal_set=self.data & other.data)

    def union(self, other: "Set") -> "Set":
        """
        Union of two sets

        Parameters
        ----------
        other: Set
            Another set object to unite

        Returns
        -------
        union: Set
            Union of two sets

        Raises
        ------
        GQLTypeError
            If given sets have different types
        """
        if self.data and other.data and self.set_type != other.set_type:
            raise GQLTypeError(f"Types mismatched: {self.set_type} != {other.set_type}")
        return Set(internal_set=self.data | other.data)

    def concatenate(self, other):
        raise NotImplementedException("Set doesn't support '.' operation, use |")

    def inverse(self):
        raise NotImplementedException("Set doesn't support 'not' operation")

    def kleene(self):
        raise NotImplementedException("Set doesn't support '*' operation")

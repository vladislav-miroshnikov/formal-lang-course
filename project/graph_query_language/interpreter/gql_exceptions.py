class RunTimeException(Exception):
    """
    Base exception for Interpreter
    """

    def __init__(self, msg: str):
        self.msg = msg


class NotImplementedException(RunTimeException):
    """
    Raises when evaluated instruction has not yet implemented
    """

    def __init__(self, instruction):
        self.msg = f"{instruction} is not implemented"


class LoadGraphException(RunTimeException):
    """
    Raises when error to load graph
    """

    def __init__(self, name: str):
        self.msg = f"Could not load graph '{name}'. Check graph name or path"


class InvalidCastException(RunTimeException):
    """
    Raises when two given types is not compatible
    """

    def __init__(self, lhs: str, rhs: str):
        self.msg = f"Invalid cast between '{lhs}' and '{rhs}'"


class VariableNotFoundException(RunTimeException):
    """
    Raises if variable is not found in Memory object
    """

    def __init__(self, name: str):
        self.msg = f"Variable name '{name}' is not defined"


class GQLTypeError(RunTimeException):
    """
    Raises if expected and actual types differ
    """

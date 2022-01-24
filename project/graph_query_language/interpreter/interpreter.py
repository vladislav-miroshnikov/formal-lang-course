import sys
from pathlib import Path

from project.graph_query_language.interpreter.gql_exceptions import (
    RunTimeException,
    InvalidScriptExtension,
    InvalidScriptPath,
)
from project.graph_query_language.interpreter.visitor import Visitor
from project.graph_query_language.parser import parse

__all__ = ["interpreter", "read_script"]


def __interpreter(input_text: str):
    """
    Internal interpreter function

    Parameters
    ----------
    input_text: str
        Program text

    Returns
    -------
    error_code: int
        0 - Success
    """
    parser = parse(text=input_text)
    tree = parser.prog()

    if parser.getNumberOfSyntaxErrors() > 0:
        raise RunTimeException(
            "Invalid syntax of program. Check the correctness of the entered text."
        )

    visitor = Visitor()
    visitor.visit(tree)

    return 0


def interpreter(*argv):
    """
    Graph Query Language interpreter runner

    Parameters
    ----------
    argv:
        0 params - Console mode. Write script in console.
        1 params - script filename. Read script with .gql extension.
        Other Parameters: Ignored

    Returns
    -------
    code: int
        Interpreter exit code

    Raises
    ------
    RunTimeException
        One of the interpreter exceptions
    """
    if len(argv[0]) == 0:
        sys.stdout.write("GQL console mode:\n===========\n")
        program = "".join(sys.stdin.readlines())
    else:
        program = read_script(filename=Path(argv[0][0]))

    return __interpreter(program)


def read_script(filename: Path) -> str:
    """
    Read script with .gql extension
    Parameters
    ----------
    filename: str
        Name of the script *.gql
    Returns
    -------
    program: str
        Script text

    Raises
    ------
    InvalidScriptPath
        Invalid path to script

    InvalidScriptExtension
        If script doesn't have .gql extension
    """
    try:
        script = filename.open()
    except FileNotFoundError as e:
        raise InvalidScriptPath(filename.name) from e

    if not filename.name.endswith(".gql"):
        raise InvalidScriptExtension()

    return "".join(script.readlines())

from project.graph_query_language.interpreter.gql_exceptions import RunTimeException
from project.graph_query_language.interpreter.visitor import Visitor
from project.graph_query_language.parser import parse

__all__ = ["interpreter"]


def interpreter(input_text: str):
    parser = parse(text=input_text)
    tree = parser.prog()

    if parser.getNumberOfSyntaxErrors() > 0:
        raise RunTimeException(
            "Invalid syntax of program. Check the correctness of the entered text."
        )

    visitor = Visitor()
    visitor.visit(tree)

    return 0

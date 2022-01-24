from project.graph_query_language.interpreter.gql_types.base_type import BaseType
from project.graph_query_language.interpreter.visitor import Visitor
from project.graph_query_language.parser import parse


def interpreter_with_value(text: str, token: str) -> BaseType:
    parser = parse(text)
    parser.removeErrorListeners()
    tree = getattr(parser, token)()
    visitor = Visitor()
    return visitor.visit(tree)

import sys

from antlr4 import InputStream, CommonTokenStream

from project.graph_query_language.GraphQueryLanguageLexer import GraphQueryLanguageLexer
from project.graph_query_language.GraphQueryLanguageParser import (
    GraphQueryLanguageParser,
)
from project.graph_query_language.interpreter.visitor import Visitor

if __name__ == "__main__":
    input_stream = InputStream(input())

    lexer = GraphQueryLanguageLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = GraphQueryLanguageParser(token_stream)
    tree = parser.prog()

    visitor = Visitor()
    b = visitor.visit(tree)
    c = 3

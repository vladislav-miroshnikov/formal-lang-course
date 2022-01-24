from antlr4 import InputStream, CommonTokenStream

from project.graph_query_language.generated.GraphQueryLanguageLexer import (
    GraphQueryLanguageLexer,
)
from project.graph_query_language.generated.GraphQueryLanguageParser import (
    GraphQueryLanguageParser,
)

__all__ = ["parse", "check_parser_correct"]


def parse(text: str) -> GraphQueryLanguageParser:
    input_stream = InputStream(text)
    lexer = GraphQueryLanguageLexer(input_stream)
    lexer.removeErrorListeners()
    stream = CommonTokenStream(lexer)
    parser = GraphQueryLanguageParser(stream)

    return parser


def check_parser_correct(text: str) -> bool:
    parser = parse(text)
    parser.removeErrorListeners()
    _ = parser.prog()
    return parser.getNumberOfSyntaxErrors() == 0

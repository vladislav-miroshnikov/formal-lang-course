from antlr4 import ParseTreeWalker, ParserRuleContext
from antlr4.error.Errors import ParseCancellationException
from antlr4.tree.Tree import TerminalNodeImpl
from pydot import Dot, Edge, Node

from project.graph_query_language.GraphQueryLanguageListener import (
    GraphQueryLanguageListener,
)
from project.graph_query_language.GraphQueryLanguageParser import (
    GraphQueryLanguageParser,
)
from project.graph_query_language.parser import parse, check_parser_correct

__all__ = ["generate_dot"]


def generate_dot(text: str, path: str):
    if not check_parser_correct(text):
        raise ParseCancellationException("The word doesn't match the grammar")
    ast = parse(text).prog()
    tree = Dot("tree", graph_type="digraph")
    ParseTreeWalker().walk(
        DotTreeListener(tree, GraphQueryLanguageParser.ruleNames), ast
    )
    tree.write(path)


class DotTreeListener(GraphQueryLanguageListener):
    def __init__(self, tree: Dot, rules):
        self.tree = tree
        self.num_nodes = 0
        self.nodes = {}
        self.rules = rules
        super(DotTreeListener, self).__init__()

    def enterEveryRule(self, ctx: ParserRuleContext):
        if ctx not in self.nodes:
            self.num_nodes += 1
            self.nodes[ctx] = self.num_nodes
        if ctx.parentCtx:
            self.tree.add_edge(Edge(self.nodes[ctx.parentCtx], self.nodes[ctx]))
        label = self.rules[ctx.getRuleIndex()]
        self.tree.add_node(Node(self.nodes[ctx], label=label))

    def visitTerminal(self, node: TerminalNodeImpl):
        self.num_nodes += 1
        self.tree.add_edge(Edge(self.nodes[node.parentCtx], self.num_nodes))
        self.tree.add_node(Node(self.num_nodes, label=f"TERM: {node.getText()}"))

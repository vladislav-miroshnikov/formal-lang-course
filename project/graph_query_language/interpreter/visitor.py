import sys
from collections import namedtuple
from typing import Union

from antlr4 import ParserRuleContext

from project.graph_query_language.generated.GraphQueryLanguageParser import (
    GraphQueryLanguageParser,
)
from project.graph_query_language.generated.GraphQueryLanguageVisitor import (
    GraphQueryLanguageVisitor,
)
from project.graph_query_language.interpreter.gql_exceptions import (
    NotImplementedException,
    GQLTypeError,
)
from project.graph_query_language.interpreter.gql_types.base_automata import (
    BaseAutomata,
)
from project.graph_query_language.interpreter.gql_types.base_type import BaseType
from project.graph_query_language.interpreter.gql_types.bool import Bool
from project.graph_query_language.interpreter.gql_types.gql_cfg import GqlCFG
from project.graph_query_language.interpreter.gql_types.finite_automata import (
    FiniteAutomata,
)
from project.graph_query_language.interpreter.gql_types.set import Set
from project.graph_query_language.interpreter.memory import Memory
from project.graph_query_language.interpreter.utils import get_graph_by_name

Fun = namedtuple("Fun", ["params", "body"])


class Visitor(GraphQueryLanguageVisitor):
    def __init__(self):
        self.memory = Memory()

    def visitProg(self, ctx: ParserRuleContext):
        return self.visitChildren(ctx)

    def visitStmt(self, ctx: GraphQueryLanguageParser.StmtContext):
        if ctx.PRINT():
            value = self.visit(ctx.expr())
            sys.stdout.write(str(value) + "\n")
        else:
            name = ctx.var().getText()
            value = self.visit(ctx.expr())
            self.memory.add_variable(name, value)

    def visitExpr(self, ctx: GraphQueryLanguageParser.ExprContext) -> BaseType:
        binary_op = {
            "AND": "intersect",
            "OR": "union",
            "DOT": "concatenate",
            "IN": "find",
        }
        unary_op = {"NOT": "inverse", "KLEENE": "kleene"}
        for b_op in binary_op:
            if getattr(ctx, b_op)():
                lhs = self.visit(ctx.expr(0))
                rhs = self.visit(ctx.expr(1))
                if b_op == "IN":
                    lhs, rhs = rhs, lhs
                return getattr(lhs, binary_op[b_op])(rhs)
        for u_op in unary_op:
            if getattr(ctx, u_op)():
                lhs = self.visit(ctx.expr(0))
                return getattr(lhs, unary_op[u_op])()

        return self.visitChildren(ctx)

    def visitGraph(self, ctx: GraphQueryLanguageParser.GraphContext) -> BaseAutomata:
        return self.visitChildren(ctx)

    def visitLoad_graph(self, ctx: GraphQueryLanguageParser.Load_graphContext):
        name = ctx.string().getText().strip('"')
        return get_graph_by_name(name)

    def _change_states(
        self,
        ctx: Union[
            GraphQueryLanguageParser.Set_startContext,
            GraphQueryLanguageParser.Set_finalContext,
            GraphQueryLanguageParser.Add_startContext,
            GraphQueryLanguageParser.Add_finalContext,
        ],
        method,
    ):
        graph = self.visit(ctx.var(0)) if ctx.var(0) else self.visit(ctx.graph())
        nodes = self.visit(ctx.var(1)) if ctx.var(1) else self.visit(ctx.vertices())
        getattr(graph, method)(nodes)

        return graph

    def visitSet_start(self, ctx: GraphQueryLanguageParser.Set_startContext):
        return self._change_states(ctx, method="set_start")

    def visitSet_final(self, ctx: GraphQueryLanguageParser.Set_finalContext):
        return self._change_states(ctx, method="set_final")

    def visitAdd_start(self, ctx: GraphQueryLanguageParser.Add_startContext):
        return self._change_states(ctx, method="add_start")

    def visitAdd_final(self, ctx: GraphQueryLanguageParser.Add_finalContext):
        return self._change_states(ctx, method="add_final")

    def visitVertex(self, ctx: GraphQueryLanguageParser.VertexContext):
        return int(ctx.INT().getText())

    def visitEdges(self, ctx: GraphQueryLanguageParser.EdgesContext):
        return self.visitChildren(ctx)

    def visitEdge(self, ctx: GraphQueryLanguageParser.EdgeContext):
        vertex_from = self.visit(ctx.vertex(0))
        label = self.visit(ctx.label())
        vertex_to = self.visit(ctx.vertex(1))
        return vertex_from, label, vertex_to

    def visitLabel(self, ctx: GraphQueryLanguageParser.LabelContext):
        return FiniteAutomata.fromString(self.visit(ctx.string()))

    def visitAnfunc(self, ctx: GraphQueryLanguageParser.AnfuncContext) -> Fun:
        params = self.visitVariables(ctx.variables())
        body = ctx.expr()
        return Fun(params=params, body=body)

    def _apply_lambda(self, fun: Fun, value: BaseType) -> BaseType:
        # TODO
        key = next(iter(fun.params))
        self.memory = self.memory.create_next_scope()
        self.memory.add_variable(key, value)
        result = self.visit(fun.body)
        self.memory = self.memory.removeLast()
        return result

    def _visit_func(
        self,
        ctx: Union[
            GraphQueryLanguageParser.MappingContext,
            GraphQueryLanguageParser.FilteringContext,
        ],
        method="map",
    ):
        anfunc = self.visit(ctx.anfunc())
        iterable = self.visit(ctx.expr())
        if not isinstance(iterable, Set):
            raise GQLTypeError(
                msg=f"Can not apply {method} on {type(iterable)} object. Set expected."
            )
        if len(iterable) == 0:
            return iterable

        first_elem = next(iter(iterable.data))
        params_count = len(first_elem.data) if isinstance(first_elem, Set) else 1
        if len(anfunc.params) != params_count:
            raise GQLTypeError(
                msg=f"Lambda argument count mismatched: Expected {len(anfunc.params)}. Got {params_count}"
            )
        # TODO
        raise NotImplementedException

    def visitMapping(self, ctx: GraphQueryLanguageParser.MappingContext):
        return self._visit_func(ctx, method="map")

    def visitFiltering(self, ctx: GraphQueryLanguageParser.FilteringContext):
        return self._visit_func(ctx, method="filter")

    def _get_graph_nodes(
        self,
        ctx: Union[
            GraphQueryLanguageParser.Select_startContext,
            GraphQueryLanguageParser.Select_finalContext,
            GraphQueryLanguageParser.Select_labelsContext,
            GraphQueryLanguageParser.Select_edgesContext,
            GraphQueryLanguageParser.Select_verticesContext,
        ],
        method,
    ):
        graph = self.visit(ctx.var()) if ctx.var() else self.visit(ctx.graph())
        return getattr(graph, method)

    def visitSelect_start(self, ctx: GraphQueryLanguageParser.Select_startContext):
        return self._get_graph_nodes(ctx, method="start")

    def visitSelect_final(self, ctx: GraphQueryLanguageParser.Select_finalContext):
        return self._get_graph_nodes(ctx, method="final")

    def visitSelect_labels(self, ctx: GraphQueryLanguageParser.Select_labelsContext):
        return self._get_graph_nodes(ctx, method="labels")

    def visitSelect_edges(self, ctx: GraphQueryLanguageParser.Select_edgesContext):
        return self._get_graph_nodes(ctx, method="edges")

    def visitSelect_vertices(
        self, ctx: GraphQueryLanguageParser.Select_verticesContext
    ):
        return self._get_graph_nodes(ctx, method="vertices")

    def visitSelect_reachable(
        self, ctx: GraphQueryLanguageParser.Select_reachableContext
    ):
        graph = self.visit(ctx.var()) if ctx.var() else self.visit(ctx.graph())
        return graph.get_reachable()

    def visitString(self, ctx: GraphQueryLanguageParser.StringContext):
        value = ctx.STRING().getText()
        return value

    def visitBoolean(self, ctx: GraphQueryLanguageParser.BooleanContext):
        return Bool(ctx.TRUE() is not None)

    def visitVar(self, ctx: GraphQueryLanguageParser.VarContext):
        name = ctx.VAR().getText()
        return self.memory.find_variable(name)

    def visitVertices_range(self, ctx: GraphQueryLanguageParser.Vertices_rangeContext):
        left_bound = int(ctx.INT(0).getText())
        right_bound = int(ctx.INT(1).getText())
        return Set(set(range(left_bound, right_bound + 1)))

    def visitVertices_set(self, ctx: GraphQueryLanguageParser.Vertices_setContext):
        if ctx.vertices_range():
            return self.visit(ctx.vertices_range())

        return Set(set(map(lambda x: int(x.getText()), ctx.INT())))

    def visitLabels_set(self, ctx: GraphQueryLanguageParser.Labels_setContext):
        labels_set = set()
        for label in ctx.STRING():
            labels_set.add(label.getText())

        return Set(labels_set)

    def visitEdges_set(self, ctx: GraphQueryLanguageParser.Edges_setContext):
        edges_set = set()
        for edge in ctx.edge():
            edges_set.add(self.visitEdge(edge))

        return Set(edges_set)

    def visitVariables(self, ctx: GraphQueryLanguageParser.VariablesContext):
        anfunc_context = {}
        if ctx.var_edge():
            raise NotImplementedException("Anfunc doesn't support var_edge")
        else:
            for v in ctx.var():
                anfunc_context[v.getText()] = None
        return anfunc_context

    def visitVar_edge(self, ctx: GraphQueryLanguageParser.Var_edgeContext):
        pass

    def visitCfg(self, ctx: GraphQueryLanguageParser.CfgContext) -> GqlCFG:
        cfg_text = ctx.CFG().getText().strip('"""')
        return GqlCFG.fromText(cfg_text)

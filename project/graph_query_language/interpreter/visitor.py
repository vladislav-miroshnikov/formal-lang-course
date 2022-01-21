from project.graph_funcs import nfa_from_graph
from project.graph_query_language.generated.GraphQueryLanguageParser import (
    GraphQueryLanguageParser,
)
from project.graph_query_language.generated.GraphQueryLanguageVisitor import (
    GraphQueryLanguageVisitor,
)
from project.graph_query_language.interpreter.interpreter_utils.GQLSet import *
from project.graph_query_language.interpreter.interpreter_utils.graph_utils import (
    load_from_disk,
    load_from_network,
)
from project.graph_query_language.interpreter.interpreter_utils.states import *
from project.graph_query_language.interpreter.interpreter_utils.type_utils import *
from project.graph_query_language.interpreter.memory import MemoryList
from project.graph_query_language.interpreter.observer import ObserverOutput
from project.matrix import BooleanMatrices


class GQLTreeVisitor(GraphQueryLanguageVisitor):
    def __init__(self, outputter: ObserverOutput):
        self.outputter = outputter
        self.memory_lst = MemoryList()
        self.output_logger = ""

    # Visit a parse tree produced by GraphQueryLanguageParser#stm.
    def visitStm(self, ctx: GraphQueryLanguageParser.StmContext):
        # bind stm
        if ctx.var():
            var_name = "empty name"
            try:
                var_name = ctx.var().IDENTIFIER().symbol.text
                value_box = self.visit(ctx.expr())
                if ctx.var().addr():
                    self.outputter.send_out(
                        "Skip addr - NOT CORRECT PLACEMENT OF ADDRESED VAR"
                    )

                self.memory_lst.set_elem(var_name, value_box)
            except InterpError as exc:
                exc.stack_lst.append(f"bind statement: [{var_name}]")
                raise exc
        # print stm
        else:
            try:
                value_box = self.visit(ctx.expr())
                self.output_logger = ">>>" + str(value_box)
                self.outputter.send_out(self.output_logger)
            except InterpError as exc:
                exc.stack_lst.append(f"print statement: [{ctx.getText()}]")
                raise exc

    # Visit a parse tree produced by GraphQueryLanguageParser#expr.
    def visitExpr(self, ctx: GraphQueryLanguageParser.ExprContext):
        flag = True

        if ctx.setVal():
            return self.visit(ctx.setVal())

        # get_reachable
        if ctx.get_reachable():
            return self.visit(ctx.get_reachable())

        # get_vertices
        if ctx.get_vertices():
            return self.visit(ctx.get_vertices())

        # get_edges
        if ctx.get_edges():
            return self.visit(ctx.get_edges())

        # get_labels
        if ctx.get_labels():
            return self.visit(ctx.get_labels())

        # mapsys
        if ctx.mapsys():
            return self.visit(ctx.mapsys())

        # filtersys
        if ctx.filtersys():
            return self.visit(ctx.filtersys())

        # star
        if ctx.star():
            return self.visit(ctx.star())

        # load graph
        if ctx.load():
            return self.visit(ctx.load())

        # val
        if ctx.val():
            try:
                value = self.visit(ctx.val())

            except InterpError as exc:
                exc.stack_lst.append("expr val")
                raise exc

            return value

        # var
        if ctx.var():
            try:
                mem_item = self.visit(ctx.var())

            except InterpError as exc:
                exc.stack_lst.append("expr var")
                raise exc

            return mem_item

        ## ---union of exprs--- ##

        # get start / final
        if ctx.get_start() or ctx.get_final():
            if ctx.get_start():
                act = "get_start"
            else:
                act = "get_final"

            try:
                if ctx.get_start():
                    source = self.visit(ctx.get_start().expr())
                else:
                    source = self.visit(ctx.get_final().expr())

                flag, exc = states_type_checker(source, act)
                if not flag:
                    raise exc

                if ctx.get_start():
                    result_set = source.value.start_states
                else:
                    result_set = source.value.final_states

            except InterpError as exc:
                if flag:
                    exc.stack_lst.append(f"expr {act}")
                raise exc

            return MemBox(True, "str", result_set)

        # set / add start
        if ctx.set_start() or ctx.add_start():
            try:
                automaton = self.visit(ctx.expr(0))
                states_set = self.visit(ctx.expr(1))
                reset = False

                if ctx.set_start():
                    reset = True

                result = set_or_add_start_states(automaton, states_set, reset)
            except InterpError as exc:
                if ctx.set_start():
                    act = "set_start"
                else:
                    act = "add_start"
                exc.stack_lst.append(f"expr {act}")
                raise exc

            return result

        # set / add final
        if ctx.set_final() or ctx.add_final():
            try:
                automaton = self.visit(ctx.expr(0))
                states_set = self.visit(ctx.expr(1))
                reset = False

                if ctx.set_final():
                    reset = True

                result = set_or_add_final_states(automaton, states_set, reset)

            except InterpError as exc:
                if ctx.set_final():
                    act = "set_final"
                else:
                    act = "add_final"
                exc.stack_lst.append(f"expr {act}")
                raise exc

            return result

        # intersect concat union
        if ctx.intersect() or ctx.concat() or ctx.union():
            act = "intersect"
            if ctx.concat():
                act = "concat"
            elif ctx.union():
                act = "union"

            try:
                first_arg = self.visit(ctx.expr(0))
                second_arg = self.visit(ctx.expr(1))

            except InterpError as exc:
                exc.stack_lst.append(f"expr prepare {act}")
                raise exc

            try:
                if ctx.intersect():
                    result = intersection(first_arg, second_arg)

                elif ctx.concat():
                    result = concatenate(first_arg, second_arg)

                else:
                    result = union(first_arg, second_arg)

            except InterpError as exc:
                exc.stack_lst.append(f"expr {act}")
                raise exc

            return result

        ## ---______________--- ##

        raise InterpError([], f"BAD command in expr: {ctx.getText()}")

    # Visit a parse tree produced by GraphQueryLanguageParser#var.
    def visitVar(self, ctx: GraphQueryLanguageParser.VarContext):
        var_name = ctx.IDENTIFIER().symbol.text
        flag = True

        if ctx.addr():

            try:
                addr_lst = self.visit(ctx.addr())
                mem_item = self.memory_lst.get_addr_elem(var_name, addr_lst)
                if not isinstance(mem_item, MemBox):
                    flag = False
                    raise InterpError(
                        ["var expr"], f"Except in addresing var: {var_name}"
                    )
            except InterpError as exc:
                exc.stack_lst.append("var expr")
                raise exc

            return mem_item

        else:

            try:
                mem_item = self.memory_lst.get_elem(var_name)
                if not isinstance(mem_item, MemBox):
                    flag = False
                    raise InterpError(
                        ["var expr pure"], f"Except in getting var memory: {var_name}"
                    )
            except InterpError as exc:
                if flag:
                    exc.stack_lst.append("var expr pure")
                raise exc

            return mem_item

    # Visit a parse tree produced by GraphQueryLanguageParser#addr.
    def visitAddr(self, ctx: GraphQueryLanguageParser.AddrContext):
        # TODO if it parsed, there no any runtime errors may occurred
        if ctx.addr():
            curr_addr = int(ctx.INT().symbol.text)
            other_lst = self.visit(ctx.addr())
            other_lst.insert(0, curr_addr)
            return other_lst
        else:
            curr_addr = int(ctx.INT().symbol.text)
            return [curr_addr]

    # Visit a parse tree produced by GraphQueryLanguageParser#val.
    def visitVal(self, ctx: GraphQueryLanguageParser.ValContext):
        # TODO if it parsed, there no any runtime errors may occurred
        if ctx.INT():
            value = int(ctx.INT().symbol.text)

        else:
            value = ctx.STRING().symbol.text[1:-1]

        return MemBox(False, "str", value)

    # Visit a parse tree produced by GraphQueryLanguageParser#setElem.
    def visitSetElem(self, ctx: GraphQueryLanguageParser.SetElemContext):
        # TODO if it parsed, there no any runtime errors may occurred
        if ctx.val():
            value = self.visit(ctx.val())
            tail = self.visit(ctx.setElem())
            tail.insert(0, value.value)
        else:
            tail = []

        return tail

    # Visit a parse tree produced by GraphQueryLanguageParser#setVal.
    def visitSetVal(self, ctx: GraphQueryLanguageParser.SetValContext):
        try:
            elements_lst = self.visit(ctx.setElem())
            result = MemBox(True, "str", elements_lst)

        except InterpError as exc:
            exc.stack_lst.append(f"expr setVal")
            raise exc

        return result

    # Visit a parse tree produced by GraphQueryLanguageParser#star.
    def visitStar(self, ctx: GraphQueryLanguageParser.StarContext):
        try:
            arg = self.visit(ctx.expr())

            try:
                result = kleene_star(arg)

            except:
                raise InterpError(["expr kleene"], "Exception in kleene_star acting")

        except InterpError as exc:
            exc.stack_lst.append("expr star")
            raise exc

        return result

    # Visit a parse tree produced by GraphQueryLanguageParser#get_reachable.
    def visitGet_reachable(self, ctx: GraphQueryLanguageParser.Get_reachableContext):
        act = "get_reachable"
        flag = True

        try:
            source = self.visit(ctx.expr())

            flag, exc = states_type_checker(source, act)
            if not flag:
                raise exc

            temp_rsm = BooleanMatrices(source.value)
            matrix_tc = temp_rsm.make_transitive_closure()

            result_set = {(i, j) for i, j in zip(*matrix_tc.nonzero())}

        except InterpError as exc:
            if flag:
                exc.stack_lst.append(f"expr {act}")
            raise exc

        return MemBox(True, "tuple 2", result_set)

    # Visit a parse tree produced by GraphQueryLanguageParser#get_vertices.
    def visitGet_vertices(self, ctx: GraphQueryLanguageParser.Get_verticesContext):
        act = "get_vertices"
        flag = True

        try:
            source = self.visit(ctx.expr())

            flag, exc = states_type_checker(source, act)
            if not flag:
                raise exc

            result_set = source.value.states

        except InterpError as exc:
            if flag:
                exc.stack_lst.append(f"expr {act}")
            raise exc

        return MemBox(True, "str", result_set)

    # Visit a parse tree produced by GraphQueryLanguageParser#get_edges.
    def visitGet_edges(self, ctx: GraphQueryLanguageParser.Get_edgesContext):
        act = "get_edges"
        flag = True

        try:
            source = self.visit(ctx.expr())

            flag, exc = states_type_checker(source, act)
            if not flag:
                raise exc

            result_set = {
                (st_from, str(label), states_to)
                for st_from, trans in source.value.to_dict().items()
                for label, states_to in trans.items()
            }

        except InterpError as exc:
            if flag:
                exc.stack_lst.append(f"expr {act}")
            raise exc

        return MemBox(True, "tuple 3", result_set)

    # Visit a parse tree produced by GraphQueryLanguageParser#get_labels.
    def visitGet_labels(self, ctx: GraphQueryLanguageParser.Get_labelsContext):
        act = "get_labels"
        flag = True

        try:
            source = self.visit(ctx.expr())

            flag, exc = states_type_checker(source, act)
            if not flag:
                raise exc

            result_set = source.value.symbols

        except InterpError as exc:
            if flag:
                exc.stack_lst.append(f"expr {act}")
            raise exc

        return MemBox(True, "str", result_set)

    # Visit a parse tree produced by GraphQueryLanguageParser#mapsys.
    def visitMapsys(self, ctx: GraphQueryLanguageParser.MapsysContext):
        flag = True

        try:
            source = self.visit(ctx.expr())

            if not isinstance(source, MemBox):
                flag = False
                raise InterpError(["expr map}"], "Source not correct internal type")
            if not source.is_list:
                flag = False
                raise InterpError(["expr map}"], "Required list source type")

            new_lst = []
            new_type = "str"

            for elem in source.value:
                if not isinstance(elem, (list, set, tuple)):
                    param = MemBox(False, "str", elem)
                else:
                    param = MemBox(True, "str", elem)

                var_name = ctx.lambdasys().var().getText()
                self.memory_lst.set_elem_stack(var_name, param)

                result = self.visit(ctx.lambdasys())

                if not isinstance(result, MemBox):
                    flag = False
                    raise InterpError(
                        ["expr map}"], "Wrong type from lambda, MemBox required"
                    )

                self.memory_lst.del_elem_stack(var_name)
                if result.is_list:
                    num = len(result.value)
                    new_type = f"tuple {num}"

                new_lst.append(result.value)

            new_box = MemBox(True, new_type, set(new_lst))

        except InterpError as exc:
            if flag:
                exc.stack_lst.append("expr map")

            raise exc

        return new_box

    # Visit a parse tree produced by GraphQueryLanguageParser#filtersys.
    def visitFiltersys(self, ctx: GraphQueryLanguageParser.FiltersysContext):
        flag = True

        try:
            source = self.visit(ctx.expr())

            if not isinstance(source, MemBox):
                flag = False
                raise InterpError(["expr filter}"], "Source not correct internal type")
            if not source.is_list:
                flag = False
                raise InterpError(["expr filter}"], "Required list source type")

            new_lst = []
            new_type = "str"

            for elem in source.value:
                if not isinstance(elem, (list, set, tuple)):
                    param = MemBox(False, "str", elem)
                else:
                    param = MemBox(True, "str", elem)

                var_name = ctx.lambdasys().var().getText()
                self.memory_lst.set_elem_stack(var_name, param)

                result = self.visit(ctx.lambdasys())

                if not isinstance(result, bool):
                    flag = False
                    raise InterpError(
                        ["expr filter}"], "Wrong type from lambda, bool required"
                    )

                self.memory_lst.del_elem_stack(var_name)

                if result:
                    if isinstance(elem, (list, set, tuple)):
                        new_lst.append(elem)
                    else:
                        new_lst.append(str(elem))

            new_box = MemBox(True, new_type, set(new_lst))

        except InterpError as exc:
            if flag:
                exc.stack_lst.append("expr filter")

            raise exc

        return new_box

    # Visit a parse tree produced by GraphQueryLanguageParser#load.
    def visitLoad(self, ctx: GraphQueryLanguageParser.LoadContext):
        path = ctx.path().STRING().symbol.text[1:-1]

        try:
            # load from disk
            if path.find(".") != -1:
                graph = load_from_disk(path)

            # load from network
            else:
                graph = load_from_network(path)

        except:
            raise InterpError(["expr load"], f"Can not load graph: {path}")

        dfa = nfa_from_graph(graph).to_deterministic()

        result_box = MemBox(False, "dfa", dfa)

        return result_box

    # Visit a parse tree produced by GraphQueryLanguageParser#lambdasys.
    def visitLambdasys(self, ctx: GraphQueryLanguageParser.LambdasysContext):
        var_name = ctx.op().var(0).IDENTIFIER().symbol.text
        flag = True
        if ctx.op().inop():

            try:
                mem_val = self.visit(ctx.op().var(0))
                mem_expr = self.visit(ctx.op().expr())

                if not isinstance(mem_val, MemBox) or not isinstance(mem_expr, MemBox):
                    flag = False
                    raise InterpError(
                        ["lambda in operator"],
                        f"Some value is not in correct internal type: {var_name}",
                    )
                if mem_val.is_list or (not mem_expr.is_list):
                    flag = False
                    raise InterpError(
                        ["lambda in operator"],
                        f"Some value is not in correct type (list/ not list): {var_name}",
                    )

                result = mem_val.value in mem_expr.value

            except InterpError as exc:
                if flag:
                    exc.stack_lst.append("lambda in operator")
                raise exc

            return result

        elif ctx.op().multop() or ctx.op().plusop():
            operator = "plus"
            if ctx.op().multop():
                operator = "multiply"

            try:
                param_lst = []
                for i in range(len(ctx.op().var())):
                    mem_val = self.visit(ctx.op().var(i))
                    param_lst.append(mem_val)

                for i in range(len(ctx.op().val())):
                    mem_val = self.visit(ctx.op().val(i))
                    param_lst.append(mem_val)

                if len(param_lst) != 2:
                    flag = False
                    raise InterpError(
                        [f"lambda {operator} operator"],
                        f"2 params required: {var_name}",
                    )
                if not isinstance(param_lst[0], MemBox) or not isinstance(
                    param_lst[1], MemBox
                ):
                    flag = False
                    raise InterpError(
                        [f"lambda {operator} operator"],
                        f"Some value is not in correct internal type: {var_name}",
                    )
                if (
                    param_lst[0].v_type != "str"
                    or param_lst[0].is_list
                    or param_lst[1].v_type != "str"
                    or param_lst[1].is_list
                ):
                    flag = False
                    raise InterpError(
                        [f"lambda {operator} operator"],
                        f"Required values type is str and not list: {var_name}",
                    )
                if not check_int(param_lst[0].value) or not check_int(
                    param_lst[1].value
                ):
                    flag = False
                    raise InterpError(
                        [f"lambda {operator} operator"],
                        f"INT required for math operations: {var_name}",
                    )

                first = int(param_lst[0].value)
                second = int(param_lst[1].value)

                if ctx.op().multop():
                    result = first * second
                else:
                    result = first + second

            except InterpError as exc:
                if flag:
                    exc.stack_lst.append(f"lambda {operator} operator")
                raise exc

            return MemBox(False, "str", str(result))

        else:

            try:
                mem_val = self.visit(ctx.op().var())

            except InterpError as exc:
                exc.stack_lst.append(f"lambda var operator")
                raise exc

            return mem_val

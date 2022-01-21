import sys

from antlr4 import *

from project.graph_query_language.generated.GraphQueryLanguageLexer import (
    GraphQueryLanguageLexer,
)
from project.graph_query_language.generated.GraphQueryLanguageParser import (
    GraphQueryLanguageParser,
)
from project.graph_query_language.interpreter.gql_exceptions import InterpError
from project.graph_query_language.interpreter.observer import ObserverOutput
from project.graph_query_language.interpreter.visitor import GQLTreeVisitor
from project.graph_query_language.parser import is_in_grammar, parse_to_string


class GQLInterpreter:
    def __init__(self, flag_info=False):
        self.outputter = ObserverOutput()
        self.out_log_list = []
        self.flag_info = flag_info
        self.visitor = GQLTreeVisitor(self.outputter)

    def run_query(self, query):
        lexer = GraphQueryLanguageLexer(InputStream(query))
        stream = CommonTokenStream(lexer)
        parser = GraphQueryLanguageParser(stream)
        tree = parser.prog()

        try:
            self.visitor.visit(tree)

        except InterpError as exc:
            self.outputter.send_out("----Exception----")
            self.outputter.send_out(exc.message)
            self.outputter.send_out("-----------------")
            for item in exc.stack_lst:
                self.outputter.send_out(item)
            self.outputter.send_out("-----------------")

        self.out_log_list = self.outputter.show()

    def online_run(self):
        raw_input = ""
        while raw_input != "exit()":
            raw_input = input(">>")

            if raw_input == "exit()":
                break
            raw_input += "\n"
            if self.flag_info:
                self.outputter.send_out("\n<<" + parse_to_string(raw_input) + ">>\n")

            if not is_in_grammar(raw_input):
                self.outputter.send_out("Error input: can not parse")
                continue

            self.run_query(raw_input)

        self.outputter.send_out("end executing")

    def file_run(self, path):
        file = open(path, "r")
        raw_input = file.read()

        if self.flag_info:
            self.outputter.send_out("\n<<" + parse_to_string(raw_input) + ">>\n")

        if not is_in_grammar(raw_input):
            self.outputter.send_out("Error input: can not parse")
            return

        self.run_query(raw_input)

        self.outputter.send_out("end executing")


if __name__ == "__main__":

    test_interp = GQLInterpreter()
    test_interp.run_query("Ig1 = load graph 'wine'\n")
    test_interp.run_query("ff = select reachable of (Ig1)\n")
    test_interp.run_query("print ff\n")

    if len(sys.argv) > 1:
        if sys.argv[1] == "online":
            interp = GQLInterpreter()
            interp.online_run()
        else:
            interp = GQLInterpreter()
            interp.file_run(sys.argv[1])

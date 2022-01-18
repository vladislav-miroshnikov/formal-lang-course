import sys

from project.graph_query_language.interpreter.interpreter import interpreter

if __name__ == "__main__":
    input_text = "".join(sys.stdin.readlines())
    interpreter(input_text)

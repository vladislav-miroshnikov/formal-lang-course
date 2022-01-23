import sys

from project.graph_query_language.interpreter.gql_exceptions import RunTimeException
from project.graph_query_language.interpreter.interpreter import interpreter


def main():
    input_text = "".join(sys.stdin.readlines())
    try:
        interpreter(input_text)
        sys.stdout.write("\nInterpreter ended with exit code 0")
        return 0
    except RunTimeException as e:
        sys.stdout.write(e.msg)
        sys.stdout.write("\nInterpreter ended with exit code 1\n")
        return 1


if __name__ == "__main__":
    main()

import sys
from typing import List

from project import graph_utils

__all__ = ["init_console"]


def exit_app() -> None:
    """
    Exit from the application

    Returns
    -------
    None
    """
    print("\nExit from the application.")
    sys.exit(0)


commands_executor = {
    "get_graph_info": graph_utils.get_graph_info_util,
    "create_two_cycles_graph": graph_utils.create_two_cycles_graph_util,
    "save_to_dot": graph_utils.save_to_dot,
    "exit": exit_app,
}


def init_console() -> None:
    """
    Starts a console application and waiting for input

    Returns
    -------
    None
    """
    print_console_info()
    while True:
        text = input(">>> ")
        try:
            execute_command(text.split(" "))
        except Exception as ie:
            print(ie.args[0])
            continue


def print_console_info():
    print("List of available commands for work:")
    print(
        "\n get_graph_info [graph_name] - get the number of nodes, edges, various labels found on the edges."
    )
    print(
        "\n create_graph [graph_name] [first_nodes_count] [second_nodes_count] [first_label] [second_label] - create "
        "graph with two cycles."
    )
    print(
        "\n save_to_dot [graph_name] [file_path] - save graph to file with .dot extension."
    )
    print("\n exit - exit from application.")


def execute_command(text_split: List[str]) -> None:
    """
    Checks that a list of strings matches an application commands and execute command

    Parameters
    ----------
    text_split: List[str]
        List of strings to check

    Returns
    -------
    None

    Raises
    ------
    Exception
        If there is no command with the same name or there is an error in the arguments
    """

    command_name = text_split[0]
    command = commands_executor.get(command_name, "default")
    if command == "default":
        raise Exception(
            f"\nCommand {command_name} is not supported, use commands from the list."
        )
    if command_name == "get_graph_info":
        if len(text_split) != 2:
            raise Exception(
                f"\nThere should be only one argument for the command {command_name}."
            )
    elif command_name == "create_two_cycles_graph":
        if len(text_split) != 6:
            raise Exception(f"\nThe number of command {command_name} must be 5.")
        if not text_split[2].isnumeric() or not text_split[3].isnumeric():
            raise Exception("\nCount of nodes must be integer value.")
    elif command_name == "save_to_dot":
        if len(text_split) != 3:
            raise Exception(
                f"\nThere should be only two argument for the command {command_name}."
            )
    command(*text_split[1:])

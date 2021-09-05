import sys
import graph_utils


def exit_app():
    print("\nExit from the application.")
    sys.exit(0)


commands_executor = {
    "get_graph_info": graph_utils.get_graph_info,
    "create_graph": graph_utils.create_graph,
    "exit": exit_app,
}


def init_console():
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
        "\n get_graph_info [name_of_graph] - get the number of nodes, edges, various labels found on the edges."
    )
    print(
        "\n create_graph [file_path] [first_nodes_count] [second_nodes_count] [first_label] [second_label] - create "
        "and save graph with two cycles to file with DOT extension."
    )
    print("\n exit - exit from application.")


def execute_command(text_split):
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
    elif command_name == "create_graph":
        if len(text_split) != 6:
            raise Exception(f"\nThe number of command {command_name} must be 5.")
        if not text_split[2].isnumeric() or not text_split[3].isnumeric():
            raise Exception("\nCount of nodes must be integer value.")

    command(*text_split[1:])

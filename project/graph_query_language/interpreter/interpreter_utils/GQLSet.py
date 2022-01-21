from pyformlang.regular_expression import Regex

from project.graph_query_language.interpreter.gql_exceptions import InterpError
from project.graph_query_language.interpreter.interpreter_utils.type_utils import (
    get_target_type,
)
from project.graph_query_language.interpreter.memory import MemBox


def kleene_star(arg):
    allow_types = ["dfa", "regex", "str"]
    worked = arg

    if isinstance(arg, str):
        worked = MemBox(False, "str", arg)

    if not isinstance(worked, MemBox):
        raise InterpError(["kleene func"], "Arg is not in correct internal type")
    if worked.v_type not in allow_types or worked.is_list:
        raise InterpError(["kleene func"], "Arg is not in allowed type for operation")

    if worked.v_type == "dfa":
        result = MemBox(
            False, "dfa", worked.value.kleene_star().to_deterministic().minimize()
        )

    else:
        worked = get_target_type(worked, "regex")
        result = MemBox(False, "regex", worked.value.kleene_star())

    return result


def concatenate(first, second):
    allow_types = ["dfa", "regex", "str"]
    f_worked = first
    s_worked = second

    if isinstance(first, str):
        f_worked = MemBox(False, "str", first)
    if isinstance(second, str):
        s_worked = MemBox(False, "str", second)

    if not isinstance(f_worked, MemBox) or not isinstance(s_worked, MemBox):
        raise InterpError(["concatenate func"], "Args are not in correct internal type")
    if (
        f_worked.v_type not in allow_types
        or s_worked.v_type not in allow_types
        or f_worked.is_list
        or s_worked.is_list
    ):
        raise InterpError(
            ["concatenate func"], "Args are not in allowed type for operation"
        )

    if f_worked.v_type == "dfa" or s_worked.v_type == "dfa":
        f_worked = get_target_type(f_worked, "dfa")
        s_worked = get_target_type(s_worked, "dfa")
        result = MemBox(False, "dfa", f_worked.value.concatenate(s_worked.value))

    else:
        f_worked = get_target_type(f_worked, "regex")
        s_worked = get_target_type(s_worked, "regex")
        result = MemBox(False, "regex", f_worked.value.concatenate(s_worked.value))

    return result


def union(first, second):
    allow_types = ["dfa", "regex", "str"]
    f_worked = first
    s_worked = second

    if isinstance(first, str):
        f_worked = MemBox(False, "str", first)
    if isinstance(second, str):
        s_worked = MemBox(False, "str", second)

    if not isinstance(f_worked, MemBox) or not isinstance(s_worked, MemBox):
        raise InterpError(["union func"], "Args are not in correct internal type")
    if (
        f_worked.v_type not in allow_types
        or s_worked.v_type not in allow_types
        or f_worked.is_list
        or s_worked.is_list
    ):
        raise InterpError(["union func"], "Args are not in allowed type for operation")

    if f_worked.v_type == "dfa" or s_worked.v_type == "dfa":
        f_worked = get_target_type(f_worked, "dfa")
        s_worked = get_target_type(s_worked, "dfa")
        result = MemBox(False, "dfa", f_worked.value.union(s_worked.value))

    else:
        f_worked = get_target_type(f_worked, "regex")
        s_worked = get_target_type(s_worked, "regex")
        result = MemBox(False, "regex", f_worked.value.union(s_worked.value))

    return result


def intersection(first, second):
    allow_types = ["dfa", "regex", "str"]
    f_worked = first
    s_worked = second

    if isinstance(first, str):
        f_worked = MemBox(False, "regex", Regex(first))
    if isinstance(second, str):
        s_worked = MemBox(False, "regex", Regex(second))

    if not isinstance(f_worked, MemBox) or not isinstance(s_worked, MemBox):
        raise InterpError(
            ["intersection func"], "Args are not in correct internal type"
        )
    if (
        f_worked.v_type not in allow_types
        or s_worked.v_type not in allow_types
        or f_worked.is_list
        or s_worked.is_list
    ):
        raise InterpError(
            ["intersection func"], "Args are not in allowed type for operation"
        )

    elif f_worked.v_type == "dfa" or s_worked.v_type == "dfa":
        f_worked = get_target_type(f_worked, "dfa")
        s_worked = get_target_type(s_worked, "dfa")
        result = MemBox(False, "dfa", f_worked.value.get_intersection(s_worked.value))

    else:
        f_worked = get_target_type(f_worked, "regex")
        s_worked = get_target_type(s_worked, "regex")
        f_enfa = f_worked.value.to_epsilon_nfa()
        s_enfa = s_worked.value.to_epsilon_nfa()
        res_dfa = f_enfa.get_intersection(s_enfa).to_deterministic().minimize()
        res_regex = res_dfa.to_regex()
        result = MemBox(False, "regex", res_regex)

    return result

import os

from pyformlang.cfg import CFG, Variable, Production, Epsilon

__all__ = ["process_wcnf_from_file", "process_wcnf_from_text", "is_weak_normal_form"]


def process_wcnf_from_file(path: str, start_symbol: str = None) -> CFG:
    """
    Process Context Free Grammar in Weak Chomsky Normal Form equivalent to file text representation of CFG.

    Parameters
    ----------
    path: str
        A path to file containing text representation of CFG with rules:
        The structure of a production is: head -> body_1 | body_2 | … | body_n
        A variable (or non terminal) begins by a capital letter
        A terminal begins by a non-capital character
        Terminals and Variables are separated by spaces
        An epsilon symbol can be represented by epsilon, $, ε, ϵ or Є
    start_symbol: str, default = None
        An axiom for CFG
        If not specified, 'S' will be used

    Returns
    -------
    CNF:
        Context Free Grammar in Weak Chomsky Normal Form equivalent to
        file text representation of CFG

    Raises
    ------
    OSError:
        If there was an error while working with file
    ValueError:
        If file text is not satisfied to the rules
    """

    if not os.path.exists(path):
        raise OSError("Incorrect file path specified: file is not exists")
    if not path.endswith(".txt"):
        raise OSError("Incorrect file path specified: *.txt is required")
    if os.path.getsize(path) == 0:
        raise OSError("Incorrect file path specified: file is empty")

    with open(path, "r") as file:
        cfg_str = file.read()

    return process_wcnf_from_text(cfg_str, start_symbol)


def process_wcnf_from_text(cfg_text: str, start_symbol: str = None) -> CFG:
    """
    Get context Free Grammar in Weak Chomsky Normal Form
    equivalent to file text representation of CFG.

    Parameters
    ----------
    cfg_text: str
        Text representation of CFG with rules:
        The structure of a production is: head -> body1 | body2 | … | bodyn
        A variable (or non terminal) begins by a capital letter
        A terminal begins by a non-capital character
        Terminals and Variables are separated by spaces
        An epsilon symbol can be represented by epsilon, $, ε, ϵ or Є
    start_symbol: str, default = None
        An axiom for CFG
        If not specified, 'S' will be used

    Returns
    -------
    WCNF:
        Context Free Grammar in Weak Chomsky Normal Form equivalent to
        file text representation of CFG

    Raises
    ------
    ValueError:
        If file text is not satisfied to the rules
    """

    if start_symbol is None:
        start_symbol = "S"

    cfg = CFG.from_text(cfg_text, Variable(start_symbol))

    wcnf = (
        cfg.remove_useless_symbols()
        .eliminate_unit_productions()
        .remove_useless_symbols()
    )

    productions = wcnf._get_productions_with_only_single_terminals()
    productions = wcnf._decompose_productions(productions)

    return CFG(start_symbol=wcnf.start_symbol, productions=set(productions))


def verify_epsilons(variables, old_productions, current_productions):
    """
    Check if all epsilons are present in the available variables from the original grammar in the given normal form.
    """
    old_productions_with_epsilon = set(
        filter(
            lambda prod: prod.head in variables and not prod.body,
            old_productions,
        )
    )

    current_productions_with_epsilon = set(
        filter(lambda prod: not prod.body, current_productions)
    )
    for production in old_productions_with_epsilon:
        if production not in current_productions_with_epsilon:
            return False
    return True


def is_weak_normal_form(cfg, cnf):
    """
    Check if a given cfg_nf is in Chomsky's minimally weakened normal form
    The rules are as follows:
    (1) A -> BC, where A, B, C in variables
    (2) A -> a, where A in variables, a in terminals
    (3) A -> epsilon, where A in variables
    It also checks if each reachable epsilon product from the original grammar is present in the WNCF.

    Parameters
    ----------
    cfg: CFG
        Original Context-Free Grammar
    cnf: CFG
        Grammar in the supposed Weak Chomsky Normal Form

    Returns
    -------
    Boolean:
        If cnf in Weak Chomsky Normal Form
    """
    for production in cnf.productions:
        body = production.body
        if not (
            (len(body) <= 2 and all(map(lambda x: x in cnf.variables, body)))
            or (len(body) == 1 and body[0] in cnf.terminals)
            or (not body)
        ) or not verify_epsilons(cnf.variables, cfg.productions, cnf.productions):
            return False
    return True

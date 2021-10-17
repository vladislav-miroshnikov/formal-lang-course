import os

from pyformlang.cfg import CFG, Variable

__all__ = ["process_cnf_from_file", "process_cnf_from_text"]


def process_cnf_from_file(path: str, start_symbol: str = None) -> CFG:
    """
    Process Context Free Grammar in Chomsky Normal Form equivalent to file text representation of CFG.

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
        Context Free Grammar in Chomsky Normal Form equivalent to
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

    return process_cnf_from_text(cfg_str, start_symbol)


def process_cnf_from_text(cfg_text: str, start_symbol: str = None) -> CFG:
    """
    Get context Free Grammar in Chomsky Normal Form (more strict case of
    the Weak Chomsky Normal Form, which can be weakened to it through product changes)
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
    CNF:
        Context Free Grammar in Chomsky Normal Form equivalent to
        file text representation of CFG

    Raises
    ------
    ValueError:
        If file text is not satisfied to the rules
    """

    if start_symbol is None:
        start_symbol = "S"

    cfg = CFG.from_text(cfg_text, Variable(start_symbol))
    cnf = cfg.to_normal_form()

    return cnf

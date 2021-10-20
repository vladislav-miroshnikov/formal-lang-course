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
    cnf = cfg.to_normal_form()

    productions = set(cfg.productions)

    if cfg.generate_epsilon():
        productions.add(Production(Variable(start_symbol), [Epsilon()]))
        wcnf = CFG(
            variables=cfg.variables,
            start_symbol=Variable(start_symbol),
            terminals=cfg.terminals,
            productions=productions,
        )
        return wcnf

    return cnf


def is_weak_normal_form(wcnf: CFG):
    """
    Checks if all products are in normal form, but allows epsilon products, that is Weak Chomsky Normal Form

    Parameters
    ----------
    wcnf: CFG

    Returns
    -------
    Boolean:
        If wcnf in Weak Chomsky Normal Form
    """

    return all(
        [
            production.is_normal_form
            for production in wcnf.productions
            if not (len(production.body) == 1 and production.body == Epsilon())
        ]
    )

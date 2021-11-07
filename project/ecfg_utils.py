from pyformlang.cfg import Variable, CFG
from pyformlang.regular_expression import Regex

from project.ecfg import ECFG, ExtendedProduction

__all__ = ["read_ecfg_from_text", "read_ecfg_from_file", "convert_cfg_to_ecfg"]


def read_ecfg_from_text(input_text, start_symbol=Variable("S")) -> "ECFG":
    """
    Read an ECFG from text

    Parameters
    ----------
    input_text: str
        Input text
    start_symbol: Variable
        Start symbol of ECFG

    Raises
    ------
    Exception:
       If there is a problem with ECFG format in text
    """
    variables = set()
    productions = set()
    for line in input_text.splitlines():
        line = line.strip()
        if not line:
            continue

        production_objects = line.split("->")

        if len(production_objects) != 2:
            raise Exception("Each line should only have one production.")

        head_text, body_text = production_objects
        head = Variable(head_text.strip())

        if head in variables:
            raise Exception("There should only be one production for each variable.")

        variables.add(head)
        body = Regex(body_text.strip())
        productions.add(ExtendedProduction(head, body))

    return ECFG(variables=variables, start_symbol=start_symbol, productions=productions)


def read_ecfg_from_file(path: str, start_symbol: str = "S") -> "ECFG":
    """
    Read an ECFG from file

    Parameters
    ----------
    path: str
        Path to file with ECFG
    start_symbol: Variable
        Start symbol of ECFG

    Raises
    ------
    Exception:
        If there is a problem with ECFG format in the text of the file
    """

    with open(path) as f:
        return read_ecfg_from_text(f.read(), start_symbol=Variable(start_symbol))


def convert_cfg_to_ecfg(cfg: CFG) -> ECFG:
    """
    Converts a CFG to an Extended CFG

    Parameters
    ---------
    cfg: CFG
        CFG to convert

    Returns
    -------
    ECFG:
        Extended CFG from CFG
    """
    productions = dict()

    for p in cfg.productions:
        body = Regex(" ".join(cfg_obj.value for cfg_obj in p.body) if p.body else "$")
        if p.head not in productions:
            productions[p.head] = body
        else:
            productions[p.head] = productions.get(p.head).union(body)

    ecfg_productions = [
        ExtendedProduction(head, body) for head, body in productions.items()
    ]

    return ECFG(
        variables=cfg.variables,
        start_symbol=cfg.start_symbol,
        productions=ecfg_productions,
    )

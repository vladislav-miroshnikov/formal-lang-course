from pyformlang.cfg import CFG

__all__ = ["convert_cfg_to_wcnf"]


def convert_cfg_to_wcnf(cfg: CFG) -> CFG:
    wcnf = (
        cfg.remove_useless_symbols()
        .eliminate_unit_productions()
        .remove_useless_symbols()
    )

    productions = wcnf._get_productions_with_only_single_terminals()
    productions = wcnf._decompose_productions(productions)

    return CFG(start_symbol=wcnf.start_symbol, productions=set(productions))

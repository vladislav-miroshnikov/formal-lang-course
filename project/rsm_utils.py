from project import RSM, ECFG, Box, regex_to_min_dfa

__all__ = ["minimize_rsm", "convert_ecfg_to_rsm"]


def minimize_rsm(rsm: RSM) -> RSM:
    """
    Minimize given RSM

    Parameters
    ----------
        rsm: RSM
            RSM to minimize

    Returns
    -------
        RSM:
            Minimized RSM
    """
    return rsm.minimize()


def convert_ecfg_to_rsm(ecfg: ECFG) -> RSM:
    """
    Converts an ECFG to a Recursive State Machine (RSM)

    Parameters
    ----------
    ecfg: ECFG
        Extended CFG to convert

    Returns
    -------
    RSM:
        Recursive state machine from ECFG.
    """
    boxes = [Box(p.head, regex_to_min_dfa(str(p.body))) for p in ecfg.productions]
    return RSM(start_symbol=ecfg.start_symbol, boxes=boxes)

import pytest
from pyformlang.cfg import CFG

from project import convert_ecfg_to_rsm, regex_to_min_dfa, convert_cfg_to_ecfg, Box, \
    minimize_rsm


@pytest.mark.parametrize(
    "cfg_text",
    [
        (
                """
                S -> B
                B -> C
                C -> S S
                S -> epsilon
                S -> a
            """),
        (
                """
                S -> a S
                S -> epsilon
            """
        ),
        (
                """
                S -> A B
                S -> epsilon
                A -> a
                B -> epsilon
            """),
    ],
)
def test_convert_ecfg_to_rsm(cfg_text):
    cfg = CFG.from_text(cfg_text)
    ecfg = convert_cfg_to_ecfg(cfg)
    rsm = convert_ecfg_to_rsm(ecfg)
    min_rsm = minimize_rsm(rsm)
    actual_start_symbol = ecfg.start_symbol
    expected_start_symbol = rsm.start_symbol
    expected_boxes = [Box(p.head, regex_to_min_dfa(str(p.body))) for p in ecfg.productions]
    actual_boxes = rsm.boxes
    assert rsm == min_rsm
    assert actual_start_symbol == expected_start_symbol \
           and actual_boxes == expected_boxes


@pytest.mark.parametrize(
    "cfg_text",
    [
        (
                """
                S -> B
                B -> C
                C -> S S
                S -> epsilon
                S -> a
            """),
        (
                """
                S -> a S
                S -> epsilon
            """
        ),
        (
                """
                S -> A B
                S -> epsilon
                A -> a
                B -> epsilon
            """),
    ],
)
def test_is_minimized_rsm(cfg_text):
    cfg = CFG.from_text(cfg_text)
    ecfg = convert_cfg_to_ecfg(cfg)
    rsm = convert_ecfg_to_rsm(ecfg)
    min_rsm = minimize_rsm(rsm)
    assert rsm == min_rsm

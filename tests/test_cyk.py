import pytest
from pyformlang.cfg import CFG

from project import cyk


@pytest.mark.parametrize(
    "cfg, words",
    [
        (
            """
                    S -> epsilon
                    """,
            ["", "epsilon", "abab"],
        ),
        (
            """""",
            ["", "epsilon"],
        ),
        (
            """
                    S -> a S b S
                    S -> epsilon
                    """,
            ["", "aba", "aabbababaaabbb", "abcd", "ab", "aaaabbbb"],
        ),
    ],
)
def test_cyk(cfg, words):
    cfg = CFG.from_text(cfg)
    assert all(cyk(cfg, word) == cfg.contains(word) for word in words)


@pytest.mark.parametrize(
    "grammar_file, words_file",
    [
        (
            "epsilon.txt",
            "epsilon_words.txt",
        ),
        (
            "empty_grammar.txt",
            "empty_words.txt",
        ),
        (
            "grammar.txt",
            "grammar_words.txt",
        ),
    ],
)
def test_cyk_from_file(grammar_file, words_file):
    grammar_path = "tests/data/cyk/" + grammar_file
    words_path = "tests/data/cyk/" + words_file
    grammar_file = open(grammar_path, "r")
    words_file = open(words_path, "r")
    words = words_file.readlines()
    words_file.close()
    grammar = grammar_file.readlines()
    grammar_file.close()
    cfg = CFG.from_text("\n".join(grammar))
    assert all(cyk(cfg, word) == cfg.contains(word) for word in words)

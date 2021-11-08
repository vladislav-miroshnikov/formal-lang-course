from pyformlang.cfg import CFG

__all__ = ["cyk"]


def cyk(cfg: CFG, word: str) -> bool:
    """
    Determines whether the given string can be generate in the given context-free grammar

    Parameters
    ---------
    cfg: CFG
        Given context-free grammar
    word: str
        Given word

    Returns
    -------
    bool
        If the given string can be generate in the given context-free grammar
    """
    word_len = len(word)

    if word_len == 0:
        return cfg.generate_epsilon()

    cnf = cfg.to_normal_form()

    d = [[set() for _ in range(word_len)] for _ in range(word_len)]

    for i in range(word_len):
        for production in cnf.productions:
            if word[i] == production.body[0].value:
                d[i][i].add(production.head.value)

    for step in range(1, word_len):
        for i in range(word_len - step):
            j = i + step
            for k in range(i, j):
                for production in cnf.productions:
                    if (
                        production.body[0].value in d[i][k]
                        and production.body[1].value in d[k + 1][j]
                    ):
                        d[i][j].add(production.head.value)
    return cnf.start_symbol.value in d[0][word_len - 1]

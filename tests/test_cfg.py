import pytest

from project.cfg import process_wcnf_from_file, is_weak_normal_form


def test_wrong_file():
    path_not_exists = "tests/data/cfg/emp"
    path_not_txt = "tests/data/cfg/empty"
    path_to_empty = "tests/data/cfg/empty.txt"

    with pytest.raises(OSError):
        process_wcnf_from_file(path_not_exists)
    with pytest.raises(OSError):
        process_wcnf_from_file(path_not_txt)
    with pytest.raises(OSError):
        process_wcnf_from_file(path_to_empty)


def test_wrong_text():
    with pytest.raises(ValueError):
        process_wcnf_from_file("tests/data/cfg/incorrect_grammar.txt")


@pytest.mark.parametrize(
    "filename, axiom",
    [("epsilon.txt", "E"), ("grammar.txt", "S"), ("random.txt", "Hello")],
)
def test_process_cnf_from_file(filename, axiom):
    path = "tests/data/cfg/" + filename

    wcnf = process_wcnf_from_file(path, axiom)

    assert is_weak_normal_form(wcnf)

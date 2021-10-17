import pytest

from project.cfg import process_cnf_from_file


def test_wrong_file():
    path_not_exists = "tests/data/cfg/emp"
    path_not_txt = "tests/data/cfg/empty"
    path_to_empty = "tests/data/cfg/empty.txt"

    with pytest.raises(OSError):
        process_cnf_from_file(path_not_exists)
    with pytest.raises(OSError):
        process_cnf_from_file(path_not_txt)
    with pytest.raises(OSError):
        process_cnf_from_file(path_to_empty)


def test_wrong_text():
    with pytest.raises(ValueError):
        process_cnf_from_file("tests/data/cfg/incorrect_grammar.txt")


@pytest.mark.parametrize(
    "filename, axiom",
    [("epsilon.txt", "epsilon"), ("grammar.txt", "S"), ("random.txt", "Hello")],
)
def test_process_cnf_from_file(filename, axiom):
    path = "tests/data/cfg/" + filename

    cnf = process_cnf_from_file(path, axiom)

    assert cnf.is_normal_form()

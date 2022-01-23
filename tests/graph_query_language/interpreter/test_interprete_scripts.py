from pathlib import Path

import pytest

from project.graph_query_language.interpreter.gql_exceptions import (
    InvalidScriptPath,
    InvalidScriptExtension,
)
from project.graph_query_language.interpreter.interpreter import (
    read_script,
    interpreter,
)


def test_invalid_file_path():
    with pytest.raises(InvalidScriptPath):
        read_script(filename=Path("invalid_path/hello.gql").absolute())


def test_invalid_extension():
    with pytest.raises(InvalidScriptExtension):
        read_script(
            filename=Path(
                "tests/graph_query_language/interpreter/scripts/invalid_extension.gqqll"
            )
        )


@pytest.mark.parametrize(
    "script_path",
    [
        "tests/graph_query_language/interpreter/scripts/labels.gql",
        "tests/graph_query_language/interpreter/scripts/labels_filter.gql",
        "tests/graph_query_language/interpreter/scripts/regex.gql",
        "tests/graph_query_language/interpreter/scripts/rpq.gql",
    ],
)
def test_correct_script(script_path):
    assert interpreter([Path(script_path)]) == 0

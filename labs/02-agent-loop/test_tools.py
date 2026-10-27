import pytest

from tools import ToolError, grep, list_files, read_file, run_tool


def test_list_files_shows_only_source_files() -> None:
    listing = list_files(".")
    for name in ("DESIGN.md", "README.md", "main.py", "test_main.py"):
        assert name in listing
    assert "uv.lock" not in listing


def test_grep_searches_every_source_file() -> None:
    matches = grep("estimate_cost")
    assert "main.py:" in matches
    assert "test_main.py:" in matches


@pytest.mark.parametrize("path", ["../../.env", "/etc/passwd", "uv.lock", ".venv/pyvenv.cfg"])
def test_read_file_refuses_anything_but_source_files(path: str) -> None:
    with pytest.raises(ToolError):
        read_file(path)


def test_list_files_refuses_other_directories() -> None:
    with pytest.raises(ToolError):
        list_files("..")


def test_invalid_regex_is_a_tool_error() -> None:
    with pytest.raises(ToolError):
        grep("(")


def test_unknown_tool_is_a_tool_error() -> None:
    with pytest.raises(ToolError):
        run_tool("write_file", {"path": "main.py"})

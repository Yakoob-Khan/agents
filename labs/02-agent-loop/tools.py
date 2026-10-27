"""The three read-only tools the model can ask for, and the code that runs them.

The model never runs these. It sends a tool_use block naming a tool and its input; the loop
in main.py calls run_tool() and sends the output back to the model as a tool_result block.
"""

import re
from pathlib import Path

from anthropic.types import ToolParam

# The only folder the tools can see: lab 01, next to this lab. Nothing above it is reachable,
# so the repo-root .env (the API key) stays out of the model's context.
ROOT = (Path(__file__).parent.parent / "01-messages").resolve()

# The only files the tools can see. Everything else in ROOT (.venv/, caches, uv.lock, config)
# isn't source code, so it never reaches the model.
SOURCE_FILES = ("DESIGN.md", "README.md", "main.py", "test_main.py")

# What the model sees of each tool: these definitions are sent with every request. The model
# picks a tool from its name and description alone, so the descriptions are prompts written
# for the model. The Python functions below are never shown to it.
#
# strict: true makes the API guarantee that every tool_use input matches input_schema, so
# the loop never receives a missing or misspelled argument. Strict schemas must list every
# property in "required" and set additionalProperties to false.
TOOL_DEFINITIONS: list[ToolParam] = [
    {
        "name": "list_files",
        "description": (
            "List the source files in a directory of the project, with each file's size in "
            "lines and bytes. The project is a small Python program with a single directory, "
            'so pass ".". Use this first to see which files exist.'
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": 'Directory to list, relative to the project root. Use ".".',
                },
            },
            "required": ["directory"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "read_file",
        "description": (
            "Read the full text of one source file. Use it once list_files or grep has shown "
            "you which file holds what you need."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": 'File path relative to the project root, e.g. "main.py".',
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "grep",
        "description": (
            "Search every source file in the project for lines matching a regular expression "
            "(Python re syntax). Returns each matching line as file:line_number: line. Use it "
            "to find where a function, variable or word appears before reading whole files."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": 'Regular expression to search for, e.g. "def estimate_cost".',
                },
            },
            "required": ["pattern"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


class ToolError(Exception):
    """A tool failed in a way the model should be told about (sent back with is_error)."""


def run_tool(name: str, arguments: dict[str, str]) -> str:
    # Dispatch on the tool name the model asked for. Thanks to strict: true, the argument
    # keys are exactly the ones in that tool's input_schema.
    if name == "list_files":
        return list_files(arguments["directory"])
    if name == "read_file":
        return read_file(arguments["path"])
    if name == "grep":
        return grep(arguments["pattern"])
    raise ToolError(f"Unknown tool {name!r}.")


def list_files(directory: str) -> str:
    if (ROOT / directory).resolve() != ROOT:
        raise ToolError(f'Cannot list {directory!r}: only the project root (".") exists.')
    lines = []
    for name in SOURCE_FILES:
        text = (ROOT / name).read_text(encoding="utf-8")
        lines.append(f"{name}  ({len(text.splitlines())} lines, {len(text.encode())} bytes)")
    return "\n".join(lines)


def read_file(path: str) -> str:
    # A tool result is text, so the file is decoded to a string, not sent as bytes.
    return source_file(path).read_text(encoding="utf-8")


def grep(pattern: str) -> str:
    try:
        regex = re.compile(pattern)
    except re.error as error:
        raise ToolError(f"Invalid regular expression {pattern!r}: {error}.") from error

    matches = []
    for name in SOURCE_FILES:
        lines = (ROOT / name).read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, start=1):
            if regex.search(line):
                matches.append(f"{name}:{number}: {line}")
    # No matches is an answer, not an error: the model learns the pattern isn't there.
    return "\n".join(matches) if matches else f"No lines match {pattern!r}."


def source_file(path: str) -> Path:
    # Resolve first, then check: "../../.env" or "/etc/passwd" become real absolute paths
    # that fail the check. Checking the raw string instead would miss tricks like "./../".
    resolved = (ROOT / path).resolve()
    if resolved.parent != ROOT or resolved.name not in SOURCE_FILES:
        allowed = ", ".join(SOURCE_FILES)
        raise ToolError(f"Cannot read {path!r}: only these files can be read: {allowed}.")
    return resolved

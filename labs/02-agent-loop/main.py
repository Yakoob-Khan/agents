"""Lab 02: a hand-written agent loop. The model explores lab 01's source code with read-only
tools until it can answer a question. Every message added to the conversation is printed.

Usage:
    uv run --env-file ../../.env main.py
    uv run --env-file ../../.env main.py "How does streaming work?"
"""

import argparse
import json
import os
import sys
from typing import cast

import anthropic
from anthropic.types import (
    Message,
    MessageParam,
    ThinkingConfigAdaptiveParam,
    ToolResultBlockParam,
    ToolUseBlock,
    Usage,
)
from pydantic import BaseModel

from tools import TOOL_DEFINITIONS, run_tool

MODEL = "claude-sonnet-5-5"

# The most output tokens the model may generate in one response (one step of the loop).
MAX_TOKENS = 16000

# The most requests one run may make. Each step of the loop is one request. Without a cap, a
# model that never decides it's done would keep calling tools (and billing) forever.
MAX_STEPS = 10

DEFAULT_QUESTION = "How is cost calculated in implementation and whether it is tested well?"

# USD per million tokens for Claude Sonnet 5.5, as of 2026-10 (same as lab 01).
# Check https://platform.claude.com/docs/en/about-claude/pricing before trusting these.
PRICE_PER_MILLION = {
    "input": 2.00,
    "output": 10.00,
    "cache_write": 2.50,
    "cache_read": 0.20,
}

# Adaptive thinking with a readable summary, as in lab 01, so each step shows what the model
# was thinking before it picked its tools.
THINKING: ThinkingConfigAdaptiveParam = {"type": "adaptive", "display": "summarized"}

# Long strings (file contents, thinking summaries) are cut to this many characters when
# printed. Only the printout is cut: the model always gets the full text.
PREVIEW_CHARS = 600

DIM = "\033[2m"  # terminal code: faint text, used for usage lines
BOLD = "\033[1m"
RESET = "\033[0m"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Let Claude explore lab 01 to answer a question.")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION, help="in quotes")
    return parser.parse_args()


def run_agent(client: anthropic.Anthropic, question: str) -> int:
    # The conversation history. The API keeps no memory between requests, so every request
    # sends this whole list, and it only ever grows: each step appends the model's response
    # and then the tool results. Nothing earlier is edited or removed.
    messages: list[MessageParam] = []
    usages: list[Usage] = []

    append(messages, {"role": "user", "content": question})

    for step in range(1, MAX_STEPS + 1):
        print(f"\n{BOLD}=== step {step}: request sends {len(messages)} messages ==={RESET}")
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            tools=TOOL_DEFINITIONS,  # sent on every request: the model sees them each time
            thinking=THINKING,
            messages=messages,
        )
        usages.append(response.usage)
        print_usage(response, usages)

        # Append the response's content whole: thinking, text and tool_use blocks, unchanged.
        # The next request must show the model exactly what it wrote, including the tool_use
        # blocks the coming tool_results answer.
        append(messages, {"role": "assistant", "content": response.content})

        # The model asks for tools by stopping with "tool_use". Any other stop reason means
        # this response is the last one:
        #   end_turn   - the model decided it has answered.
        #   max_tokens - cut off at MAX_TOKENS. A tool_use block may be cut off mid-input,
        #                so never run its tools.
        #   refusal    - the model declined. Never run a refused turn's tools either.
        #   pause_turn - only comes from server-side tools, which this lab doesn't use.
        if response.stop_reason != "tool_use":
            return report(response, usages)

        # Run every tool the model asked for in this response. There may be several
        # (parallel tool calls); they run one after another here, since each takes
        # microseconds. How they run is invisible to the model.
        tool_results = [
            execute(block) for block in response.content if isinstance(block, ToolUseBlock)
        ]

        # All results for this response go back together in ONE user message. Each result
        # names the tool_use block it answers by tool_use_id.
        append(messages, {"role": "user", "content": tool_results})

    # The cap was hit: the last tool results were appended but never sent to the model.
    print(f"\n{BOLD}=== stopped: reached MAX_STEPS ({MAX_STEPS}) ==={RESET}")
    return report(response, usages, cap_reached=True)


def execute(block: ToolUseBlock) -> ToolResultBlockParam:
    # strict: true guarantees block.input matches the tool's input_schema: an object whose
    # values are all strings, for these three tools.
    arguments = cast(dict[str, str], block.input)
    try:
        output = run_tool(block.name, arguments)
    except Exception as error:
        # A failing tool must not crash the loop. The error goes back to the model as the
        # result, marked is_error, so it can try a different path or tool.
        return {
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": f"Error: {error}",
            "is_error": True,
        }
    return {"type": "tool_result", "tool_use_id": block.id, "content": output}


def append(messages: list[MessageParam], message: MessageParam) -> None:
    # Every change to the history goes through here, so the printout is exactly the diff
    # added to the conversation, in the JSON shape the API receives.
    messages.append(message)
    print(f"\n+ messages[{len(messages) - 1}] ({message['role']}):")
    print(json.dumps(shorten(plain(message)), indent=2, ensure_ascii=False))


def plain(message: MessageParam) -> dict[str, object]:
    # The model's blocks are SDK objects; the tool results are dicts. Turn both into plain
    # data for printing.
    content = message["content"]
    if isinstance(content, str):
        return {"role": message["role"], "content": content}
    blocks = [
        block.model_dump(exclude_none=True) if isinstance(block, BaseModel) else dict(block)
        for block in content
    ]
    return {"role": message["role"], "content": blocks}


def shorten(value: object) -> object:
    if isinstance(value, dict):
        # A thinking block's signature is a long encrypted string. It must be sent back
        # unchanged, but it's unreadable, so only its length is printed.
        return {
            key: f"<{len(item)} chars>" if key == "signature" else shorten(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [shorten(item) for item in value]
    if isinstance(value, str) and len(value) > PREVIEW_CHARS:
        return f"{value[:PREVIEW_CHARS]}... [{len(value) - PREVIEW_CHARS} more chars not shown]"
    return value


def estimate_cost(usage: Usage) -> float:
    # Same as lab 01: tokens x price, per token type. Cached tokens are counted separately.
    cache_write = usage.cache_creation_input_tokens or 0
    cache_read = usage.cache_read_input_tokens or 0
    dollars = (
        usage.input_tokens * PRICE_PER_MILLION["input"]
        + usage.output_tokens * PRICE_PER_MILLION["output"]
        + cache_write * PRICE_PER_MILLION["cache_write"]
        + cache_read * PRICE_PER_MILLION["cache_read"]
    )
    return dollars / 1_000_000


def print_usage(response: Message, usages: list[Usage]) -> None:
    # Input tokens grow every step: each request resends the whole history.
    usage = response.usage
    total = sum(estimate_cost(u) for u in usages)
    print(
        f"{DIM}stop_reason: {response.stop_reason} | input {usage.input_tokens} tokens, "
        f"output {usage.output_tokens} | step ${estimate_cost(usage):.4f}, "
        f"run so far ${total:.4f}{RESET}"
    )


def report(response: Message, usages: list[Usage], cap_reached: bool = False) -> int:
    # "Print what we have": the text of the model's last response, whatever ended the run.
    answered = response.stop_reason == "end_turn" and not cap_reached
    if answered:
        print(f"\n{BOLD}=== answer ==={RESET}")
    else:
        print(f"\n{BOLD}=== no final answer (stop_reason: {response.stop_reason}) ===")
        print(f"what the model wrote in its last response:{RESET}")
        if response.stop_details is not None:
            print(f"stop_details: {response.stop_details}")

    text = "\n".join(block.text for block in response.content if block.type == "text")
    print(text or "(no text)")

    print(f"\n{BOLD}=== run totals ==={RESET}")
    print(f"requests:      {len(usages)}")
    print(f"input tokens:  {sum(u.input_tokens for u in usages)} (summed over all requests)")
    print(f"output tokens: {sum(u.output_tokens for u in usages)}")
    print(f"approx cost:   ${sum(estimate_cost(u) for u in usages):.4f}")
    return 0 if answered else 1


def main() -> int:
    args = parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set. See labs/02-agent-loop/README.md.", file=sys.stderr)
        return 1

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    try:
        return run_agent(client, args.question)
    except anthropic.AuthenticationError:
        print("The API rejected the key (401). Check ANTHROPIC_API_KEY in .env.", file=sys.stderr)
    except anthropic.APIStatusError as error:
        print(f"API error {error.status_code}: {error.message}", file=sys.stderr)
    except anthropic.APIConnectionError:
        print("Could not reach the API. Check your network connection.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

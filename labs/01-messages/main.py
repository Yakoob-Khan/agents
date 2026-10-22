"""Lab 01: send one prompt to Claude, print the answer, then the response metadata.

Usage:
    uv run --env-file ../../.env main.py "What is a context window?"
    uv run --env-file ../../.env main.py --effort low "What is a context window?"
"""

import argparse
import os
import sys
import time
from typing import Literal, get_args

import anthropic
from anthropic import Omit, omit
from anthropic.types import Message, MessageParam, OutputConfigParam, Usage

MODEL = "claude-sonnet-5-5"

# The most output tokens the model may generate for this one response. If it hits this
# limit it is cut off mid-answer (try a tiny value as a break-it experiment).
MAX_TOKENS = 16000

Effort = Literal["low", "medium", "high", "xhigh", "max"]
EFFORT_LEVELS = list(get_args(Effort))
DEFAULT_EFFORT: Effort = "high"  # what Claude Sonnet 5.5 uses when the request doesn't set effort

# USD per million tokens for Claude Sonnet 5.5, as of 2026-10.
# Check https://platform.claude.com/docs/en/about-claude/pricing before trusting these.
PRICE_PER_MILLION = {
    "input": 2.00,
    "output": 10.00,
    "cache_write": 2.50,  # 1.25x input, for the default 5-minute cache
    "cache_read": 0.20,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask Claude one question.")
    parser.add_argument("prompt", help="the question to ask, in quotes")
    parser.add_argument(
        "--effort",
        choices=EFFORT_LEVELS,
        default=None,
        help=f"how much effort the model spends (default: model default, {DEFAULT_EFFORT})",
    )
    return parser.parse_args()


def ask(client: anthropic.Anthropic, prompt: str, effort: Effort | None) -> Message:
    # The whole conversation is sent on every request: the API keeps no memory between
    # calls. Here the conversation is a single user message.
    messages: list[MessageParam] = [{"role": "user", "content": prompt}]

    # `omit` leaves output_config out of the request body entirely, so the model uses its
    # default effort. Thinking is also left unset: Claude Sonnet 5.5 then decides for
    # itself how much to think (adaptive thinking).
    output_config: OutputConfigParam | Omit = omit if effort is None else {"effort": effort}

    return client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=messages,
        output_config=output_config,
    )


def estimate_cost(usage: Usage) -> float:
    # The API returns token counts, not dollars: cost is tokens x price, per token type.
    # input_tokens excludes cached tokens, which are counted (and priced) separately.
    cache_write = usage.cache_creation_input_tokens or 0
    cache_read = usage.cache_read_input_tokens or 0
    dollars = (
        usage.input_tokens * PRICE_PER_MILLION["input"]
        + usage.output_tokens * PRICE_PER_MILLION["output"]
        + cache_write * PRICE_PER_MILLION["cache_write"]
        + cache_read * PRICE_PER_MILLION["cache_read"]
    )
    return dollars / 1_000_000


def print_answer(response: Message) -> None:
    # The response content is a list of blocks. Only "text" blocks are the visible answer;
    # others (e.g. "thinking") are printed in the metadata section instead.
    for block in response.content:
        if block.type == "text":
            print(block.text)


def print_metadata(response: Message, effort: Effort | None, latency_seconds: float) -> None:
    print("\n--- response metadata ---")
    print(f"id:             {response.id}")
    print(f"request id:     {response._request_id}")
    print(f"model:          {response.model}")
    print(f"stop_reason:    {response.stop_reason}")
    if response.stop_details is not None:
        print(f"stop_details:   {response.stop_details}")
    print(f"content blocks: {[block.type for block in response.content]}")
    print(f"effort sent:    {effort or f'(not set, model default: {DEFAULT_EFFORT})'}")

    print("\n--- usage (everything the API reports) ---")
    print(response.usage.model_dump_json(indent=2, exclude_none=True))

    print("\n--- measured by this script ---")
    print(f"approx cost:    ${estimate_cost(response.usage):.6f}")
    print(f"latency:        {latency_seconds:.2f}s")


def main() -> int:
    args = parse_args()
    effort: Effort | None = args.effort  # argparse already limited it to EFFORT_LEVELS

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set. See labs/01-messages/README.md.", file=sys.stderr)
        return 1

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    start = time.perf_counter()
    try:
        response = ask(client, args.prompt, effort)
    except anthropic.AuthenticationError:
        print("The API rejected the key (401). Check ANTHROPIC_API_KEY in .env.", file=sys.stderr)
        return 1
    except anthropic.APIStatusError as error:
        print(f"API error {error.status_code}: {error.message}", file=sys.stderr)
        return 1
    except anthropic.APIConnectionError:
        print("Could not reach the API. Check your network connection.", file=sys.stderr)
        return 1
    latency_seconds = time.perf_counter() - start

    print_answer(response)
    print_metadata(response, effort, latency_seconds)
    return 0


if __name__ == "__main__":
    sys.exit(main())

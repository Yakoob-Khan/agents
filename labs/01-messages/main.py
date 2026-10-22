"""Lab 01: stream one prompt's answer from Claude, then print the response metadata.

Usage:
    uv run --env-file ../../.env main.py "What is a context window?"
    uv run --env-file ../../.env main.py --effort low "What is a context window?"
"""

import argparse
import os
import sys
import time
from collections import Counter
from dataclasses import dataclass
from typing import Literal, get_args

import anthropic
from anthropic import Omit, omit
from anthropic.types import (
    Message,
    MessageParam,
    OutputConfigParam,
    ThinkingConfigAdaptiveParam,
    Usage,
)

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

# The event types the API itself sends over the stream. The SDK also yields extra
# convenience events (e.g. "text", "thinking") built from these; we don't count those.
API_EVENT_TYPES = {
    "message_start",
    "content_block_start",
    "content_block_delta",
    "content_block_stop",
    "message_delta",
    "message_stop",
}

THINKING_INDICATOR = "Thinking..."
CLEAR_LINE = "\r\033[K"  # terminal codes: return to the start of the line, then erase it
DIM = "\033[2m"  # terminal code: faint text, used for the thinking summary
RESET = "\033[0m"  # terminal code: back to normal text


@dataclass
class StreamResult:
    message: Message  # the full response, assembled by the SDK from the events
    request_id: str | None  # from the HTTP response headers; a streamed message lacks it
    first_thinking_seconds: float | None  # time to first thinking summary text; None if none
    first_text_seconds: float | None  # time to first answer text; None if none arrived
    total_seconds: float
    event_counts: Counter[str]


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


def stream_answer(client: anthropic.Anthropic, prompt: str, effort: Effort | None) -> StreamResult:
    # The whole conversation is sent on every request: the API keeps no memory between
    # calls. Here the conversation is a single user message.
    messages: list[MessageParam] = [{"role": "user", "content": prompt}]

    # `omit` leaves output_config out of the request body entirely, so the model uses its
    # default effort.
    output_config: OutputConfigParam | Omit = omit if effort is None else {"effort": effort}

    # Adaptive thinking: the model decides for itself whether and how much to think.
    # display "summarized" asks the API to send a readable summary of the thinking.
    # The default on Claude Sonnet 5.5 is "omitted": the thinking block arrives empty.
    # Either way, the full thinking is generated and billed the same.
    thinking: ThinkingConfigAdaptiveParam = {"type": "adaptive", "display": "summarized"}

    event_counts: Counter[str] = Counter()
    first_thinking_seconds: float | None = None
    first_text_seconds: float | None = None

    print(THINKING_INDICATOR, end="", flush=True)
    start = time.perf_counter()

    # Same request as before, but the response arrives as a sequence of events while the
    # model is still generating, instead of one finished message at the end.
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=messages,
        output_config=output_config,
        thinking=thinking,
    ) as stream:
        for event in stream:
            if event.type in API_EVENT_TYPES:
                event_counts[event.type] += 1
            if event.type != "content_block_delta":
                continue

            # The thinking summary arrives in pieces ("thinking_delta"s) inside the
            # thinking block, which always comes before the answer's text block.
            if event.delta.type == "thinking_delta":
                if first_thinking_seconds is None:
                    first_thinking_seconds = time.perf_counter() - start
                    print(f"{CLEAR_LINE}{DIM}[thinking summary]\n", end="")
                print(event.delta.thinking, end="", flush=True)

            # Answer text arrives in pieces ("text_delta"s) inside a text block.
            elif event.delta.type == "text_delta":
                if first_text_seconds is None:
                    first_text_seconds = time.perf_counter() - start
                    if first_thinking_seconds is None:
                        print(CLEAR_LINE, end="")  # erase "Thinking..." before the answer
                    else:
                        print(f"{RESET}\n\n[answer]\n", end="")  # end the faint summary
                print(event.delta.text, end="", flush=True)

        # The SDK has been assembling the events into one Message as they arrived: the
        # same object the non-streaming call returned, with the final usage and stop_reason.
        message = stream.get_final_message()
        request_id = stream.request_id

    total_seconds = time.perf_counter() - start
    if first_text_seconds is not None:
        print()
    elif first_thinking_seconds is not None:
        print(RESET)  # cut off while thinking: end the faint summary text
    else:
        print(CLEAR_LINE, end="")  # nothing visible arrived: erase "Thinking..."

    return StreamResult(
        message,
        request_id,
        first_thinking_seconds,
        first_text_seconds,
        total_seconds,
        event_counts,
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


def print_metadata(result: StreamResult, effort: Effort | None) -> None:
    response = result.message
    print("\n--- response metadata ---")
    print(f"id:             {response.id}")
    print(f"request id:     {result.request_id}")
    print(f"model:          {response.model}")
    print(f"stop_reason:    {response.stop_reason}")
    if response.stop_details is not None:
        print(f"stop_details:   {response.stop_details}")
    print(f"content blocks: {[block.type for block in response.content]}")
    print(f"effort sent:    {effort or f'(not set, model default: {DEFAULT_EFFORT})'}")

    print("\n--- usage (everything the API reports) ---")
    print(response.usage.model_dump_json(indent=2, exclude_none=True))

    print("\n--- stream events received (from the API) ---")
    for event_type, count in result.event_counts.items():
        print(f"{event_type:<20} {count}")

    print("\n--- measured by this script ---")
    print(f"approx cost:       ${estimate_cost(response.usage):.6f}")
    if result.first_thinking_seconds is not None:
        print(f"first thinking:    {result.first_thinking_seconds:.2f}s")
    if result.first_text_seconds is None:
        print("first answer text: (none arrived)")
    else:
        print(f"first answer text: {result.first_text_seconds:.2f}s")
    print(f"total latency:     {result.total_seconds:.2f}s")


def fail(message: str) -> int:
    print(f"{RESET}{CLEAR_LINE}", end="", flush=True)  # normal text; erase "Thinking..."
    print(message, file=sys.stderr)
    return 1


def main() -> int:
    args = parse_args()
    effort: Effort | None = args.effort  # argparse already limited it to EFFORT_LEVELS

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set. See labs/01-messages/README.md.", file=sys.stderr)
        return 1

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    try:
        result = stream_answer(client, args.prompt, effort)
    except anthropic.AuthenticationError:
        return fail("The API rejected the key (401). Check ANTHROPIC_API_KEY in .env.")
    except anthropic.APIStatusError as error:
        return fail(f"API error {error.status_code}: {error.message}")
    except anthropic.APIConnectionError:
        return fail("Could not reach the API. Check your network connection.")

    print_metadata(result, effort)
    return 0


if __name__ == "__main__":
    sys.exit(main())

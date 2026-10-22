# L1 — Messages: design

> Status: draft (scope checked; awaiting approval)

## Goal
A command line program that sends one prompt to Claude and prints the answer, followed by the response metadata, so I can see what a model API request and response look like.

## Scope
- In:
  - "I will start simple and just have the command line script accept one argument in quotes as the prompt that the user wants to ask the LLM."
  - "To keep things simple, I will have the script print the output to the terminal, and after the LLM response, have the effort, tokens used, and metrics that the API response exposes printed out for visibility."
  - "I want to print the approximate cost of making the query, and the latency by having a start and stop (for non streaming setting that we are working on for this lab)."
  - "Once I have a simple command line program built that fully prints out the model response with the metadata from the API response, I will then work on streaming the answer and structured JSON output."
- Out (and saved for later): conversation history / multi-turn (Phase 2), tools (L2).

## How I think it works
My guesses before building:

- **What is sent in each request?** "I don't know about the API request body shape. I guess information like the prompt, model name, system prompt, effort, will be attributes in the API request body."
- **What comes back?** "I don't know what API response shape looks like."
- **Does a second call remember the first?** "I don't think the 2nd call will remember the first call without the 2nd call passing in the 1st response as context to the 2nd call input."
- **What makes the model stop?** "After the first response is returned, I think the model stops. I actually don't understand what makes the model stop question really means."
- **What changes between low and high effort?** "The latency time will change between the low and high effort."

```
user (prompt as CLI argument) → script → Claude API → response → script prints answer, then metadata, cost, latency
```

## Components
| Piece | Responsibility |
|---|---|
| CLI script | Accepts one quoted prompt argument and an optional effort flag |
| API call | Sends the request to Claude (non-streaming for step 1) |
| Output | Prints the answer, then the response metadata, tokens used, approximate cost, and latency |

## Tools / prompts / data
- No tools.
- Model: "use sonnet 5.5 as the model with the default effort level that anthropic advertises."
- Effort: "I will have the default effort. The command line program will expose an optional flag that lets the user configure the effort level to pass in the request body."
- API key: "I have a claude API key subscription that I want to load as an environment variable so that I can do these exercises and make a query to a cheap Claude model."

## Open questions
- What the request and response bodies look like (to be seen when built).

## Decisions
- **Model:** Claude Sonnet 5.5 (`claude-sonnet-5-5`), at Anthropic's default effort unless the flag is passed.
- **Build order:** "Once I have a simple command line program built that fully prints out the model response with the metadata from the API response, I will then work on streaming the answer and structured JSON output."
- **Tooling (D12):** "I will use Python 3.12 as I think this is the industry latest. I think of using `uv` as this is the industry standard python package manager for managing dependencies." Linting, type checking, and tests: "uv + Ruff + mypy + pytest".

## Done when
- [ ] Step 1: one quoted prompt in; the answer printed, then the response metadata, tokens used, approximate cost, and latency.
- [ ] Optional effort flag works.
- [ ] Step 2: the answer streams.
- [ ] Step 3: structured JSON output.
- [ ] Break-it experiments run: low vs high effort; a tiny `max_tokens`.

## Retro
After building: what surprised me, what I'd change.

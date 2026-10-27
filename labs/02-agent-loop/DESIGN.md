# L2 — Agent loop: design

> Status: draft

## Goal
A hand-written agent loop that gives the model read-only tools over the lab 01 source code and lets it explore until it can answer a question, so I can see how tool use and the loop work.

## Scope
- In:
  - Source code: "Just use lab 1 as the source code."
  - Source files are "main.py, test_main.py, README.md, DESIGN.md." only.
  - Question: "how is cost calculated in implementation and whether it is tested well"
  - Three read-only tools: list files, read file, grep (folder wide).
  - A turn limit, and printing each iteration of the loop.
- Out (and saved for later):
  - Asking the user for permission to read outside the directory: "The agent would need to ask the user for permission if it wants to read outside the directory it has been launched in. I know claude agent stops, asks the user for permission, then continues. perhaps this is more sophisticated than the version needed for lab 2." → M2 (permission as a protocol). In L2 the tools refuse such paths.
  - Tools that write files or run commands → M2.

## How I think it works
My guesses before building:

- **Tools:** "My understanding is that tools are basically functions. The doc string should be well written as that serves as prompt for the model to know which tool call to make to get useful outputs to answer the original question."
- **List files:** "List files will take a root directory, and it's implementation can use create a similar output to what the terminal `ls` command does."
- **Read file:** "read files takes a file input and outputs the file bytes, which python IO library can be used to read the string."
- **Grep:** "grep tool can be used to find string search matching in a specific file content." (Later decided: folder wide.)
- **When the loop stops:** "The loop will terminate when the model outputs a stop_turn where the model has decided it has answered the initial prompt question. Until then, the model keeps outputting tool calls to answer the user question. The loop could also have a limit of the number of turns to prevent infinite looping."
- **Results going back:** "The output gets back to the model by appending to the conversation history. Not sure what the exact structure of the API body request / response looks like."
- **Matching results to calls:** "For each tool use, there should be tool_result, 1-to-1 mapping. Key value pair so model knows the outcome of each tool call."
- **Parallel calls:** "Parallel tool calls can happen on multi-threading."
- **Errors:** "good tool implementations should have good error handling so the model knows if the tool call raised an error."
- **Input schema:** "by having JSON input schema, we can force the model to generate output in a schema we expect."

```
user question → loop → model → tool calls → loop runs tools → tool results appended to history → model → ... → end_turn → answer
```

## Components
| Piece | Responsibility |
|---|---|
| Tool definitions | Name, description and input schema for each tool, sent to the model with every request |
| Tool functions | `list_files`, `read_file`, `grep`: read-only, scoped to `labs/01-messages/`, only the four source files |
| Loop | Sends the history, checks `stop_reason`, runs requested tools, appends results, repeats up to the cap |
| Output | Prints each iteration: what was added to the history, the tool calls, the tool results |

## Tools / prompts / data
- **Tools:** `list_files`, `read_file`, `grep` (folder wide).
- **Data:** "ignore .venv directory. those are dependency versioning files, not source code." "ignore all the system cache files." Source files are "main.py, test_main.py, README.md, DESIGN.md." only.
- **Stack:** "keep L1's tech stack. I want to focus on the concepts." (Sonnet 5.5 at default effort, Python 3.12, uv, Ruff, mypy, pytest, `.env`.)

## Open questions
- What the request and response bodies look like with tools (to be seen when built).

## Decisions
- **Source code:** lab 01, limited to `main.py`, `test_main.py`, `README.md`, `DESIGN.md`. Everything else (`.venv/`, caches, `uv.lock`, config files) is ignored.
- **Grep:** "grep folder wide."
- **Paths outside `labs/01-messages/`:** refused, with the refusal returned as an error tool result. Permission prompts are M2.
- **Results:** each `tool_result` carries the `tool_use_id` of its call; all results from one model response go back in one user message.
- **Errors:** returned to the model as a tool result with `is_error: true`; the loop continues.
- **Inputs:** tool definitions use `strict: true` so inputs always match the schema.
- **Stopping:** `end_turn` → print the answer. "Print what we have" if the cap is reached, and the same for `max_tokens` and `refusal`.
- **Output:** "I want to print the tool call, tool result, what the model input, output was at each step." For the input: "print only the diff being added to the conversation history."

## Misconceptions corrected
Where my guesses above were wrong, and what's actually true:

1. **Docstring as the prompt.** With the raw SDK the model never sees the Python docstring. Each tool is sent as a definition in the request: `name`, `description` (the part that acts as the prompt), and `input_schema` (JSON Schema). The Python function is just what my loop calls when the model asks for that name. Frameworks generate the definition from the docstring.
2. **`stop_turn`.** The value is `end_turn`. Other stop reasons: `tool_use` (run tools and go again), `max_tokens`, `pause_turn`, `refusal`. The loop has to handle each.
3. **Read file outputs bytes.** A tool result is text, so the file is decoded to a string.
4. **"How does streaming work" needs the test files.** `test_main.py` only tests `estimate_cost`; it never touches streaming. That's why the question changed to cost.
5. **Key value pair.** The pairing is the `tool_use_id`: each `tool_use` block has an `id`, and its `tool_result` names it. When the model asks for several tools in one response, all results go back together in one user message.
6. **Parallel calls are multi-threading.** Threads (or asyncio) only decide how my loop runs the tools. The model never sees that; what it sees is all the results arriving in one message.
7. **Error handling.** The model learns a tool failed when the result text is the error and the block has `is_error: true`. The loop doesn't crash; the model can retry or try something else.
8. **The JSON input schema forces the shape.** On its own, the schema is followed most of the time but not guaranteed. `strict: true` on the tool definition is what guarantees it.
9. **Who "Claude" is.** In this lab, "Claude" is the model answering my API request, not Claude Code. The agent is my Python loop. The model only asks for tools; my loop runs them.

## Done when
- [ ] Asking the cost question makes the model explore with tools and answer from `main.py` and `test_main.py`.
- [ ] Each iteration prints what was added to the history, the tool calls and the tool results.
- [ ] A path outside `labs/01-messages/` comes back as an error result, not a crash.
- [ ] Hitting the cap, `max_tokens` or `refusal` prints what we have.
- [ ] Break-it experiments run: vague tool description; tool returns an error; parallel results split across two messages; no iteration cap + impossible task.
- Skipped: the 50k-token tool result (token cost). Instead, watch input tokens grow each step in normal runs: the whole history is resent on every request.

## Retro
After building: what surprised me, what I'd change.

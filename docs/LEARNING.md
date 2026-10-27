# LEARNING — concepts I understand

> What I've learned, in my own words, after building it. Append-mostly. My personal knowledge base for the series.
> After each milestone: prompt Claude *"add what I learned to LEARNING.md"* and dictate it — not pasted from docs.
> Companion: [`PLAN.md`](PLAN.md) (what to do) · [`WORKFLOW.md`](WORKFLOW.md) (how) · [`DECISIONS.md`](DECISIONS.md) (why)

Each entry: **what it is** (one or two sentences) · **what I saw when I built it** · **when I'd use it / not** · **milestone link**.

---

## Agent fundamentals (labs)

### The Messages API
> _what's in a request, stop reasons, tokens, streaming_

**Stop reasons.** The API response has a `stop_reason` that tells why the model stopped generating text.
- `end_turn`: the model decided to stop for itself.
- `max_tokens`: specifying max tokens cuts off the output.

What I saw: with `MAX_TOKENS = 50`, the answer was cut off at exactly 50 output tokens and `stop_reason` was `max_tokens`. ([L1](../labs/01-messages/DESIGN.md))

**Streaming.** Streaming events improves UX: the answer shows up while the model is still generating, instead of after the whole response is done. It doesn't change the total time or the cost.

What I saw: the simple question showed its first answer text at 0.92s instead of waiting the full 5.05s. ([L1](../labs/01-messages/DESIGN.md))

**Blocks and deltas.** There are different kinds of blocks in a response: thinking, text. Each block has deltas: a delta is one event carrying the next piece of that block.

What I saw: the hard question streamed 2 blocks (thinking, then text) as 466 `content_block_delta` events, wrapped in `content_block_start` / `content_block_stop` for each block. ([L1](../labs/01-messages/DESIGN.md))

### Thinking & effort
> _adaptive thinking; what effort trades off_

**Thinking tokens.** There are thinking tokens besides the answer: the model's reasoning before it writes the answer. They count inside `output_tokens` (reported separately in `output_tokens_details.thinking_tokens`).

What I saw: a simple question used 0 thinking tokens; a harder question used 719 thinking tokens out of 2,485 output tokens. ([L1](../labs/01-messages/DESIGN.md))

### The agent loop & tool use
> _the loop, tool definitions, tool_use / tool_result_

**The agent loop.** "The agent loop sends the list of tools names and description, the model makes tool use responses if it wants to use the list of available tools to answer the question, the agent loop executes the respective tool, adds the tool result to the input for the next time the LLM request is made, iteratively until the model issues an end turn and is satified that it has answered the user's question."

What I saw: asking "How is cost calculated in implementation and whether it is tested well?" took 3 requests ($0.035). Request 1 → `list_files` + `grep`, request 2 → `read_file` × 2 (`main.py`, `test_main.py`), request 3 → `end_turn` with the answer. Input tokens grew 763 → 1,760 → 6,536. ([L2](../labs/02-agent-loop/DESIGN.md) · visual: [`agent-loop.html`](../labs/02-agent-loop/agent-loop.html))

**Terms I missed in my summary:**
- **`input_schema`:** each tool definition is `name` + `description` + `input_schema` (JSON Schema for its inputs). `strict: true` guarantees the model's inputs match the schema.
- **The whole history is sent every time:** every request resends every earlier message, not just the latest result. That's why input tokens grow each step.
- **Two messages appended per step:** first the model's response (its `tool_use` blocks, appended whole), then a user message with the `tool_result` blocks.
- **`tool_use_id`:** each `tool_use` block has an `id`; its `tool_result` carries the same value as `tool_use_id`. That's how the model knows which result answers which call.
- **Parallel tool calls:** one response can hold several `tool_use` blocks. All their results go back together in one user message.
- **`is_error`:** a failed tool still returns a `tool_result`, with the error as its content and `is_error: true`, so the model can try something else.
- **The loop can also end it:** besides `end_turn`, the loop stops on a step cap (`MAX_STEPS`), `max_tokens`, or `refusal`, and prints what it has. It never runs tools from a cut-off or refused turn.

**The agent loop, in one paragraph (end of L2).** "Agent loop is about providing a list of tools to the LLM with each LLM request, letting the model pick tools to call, the agent executes the tool, appends the tool result to the growing conversation history, model doesn't hold agents conversation state, and model decides end_turn when it answers the question, or max cap is reached. tool caps prevent context from being overloaded with too much info."

Notes:
- The model only ends a run with `end_turn`. The max cap (`MAX_STEPS`), `max_tokens` and `refusal` are the loop stopping it from outside.
- Two different caps: the step cap limits how many requests (and roughly the cost); a tool result size cap limits how much one result adds to the context. L2 has only the step cap; the files were small enough not to need the other (retro hole, comes back in M2).

**Impossible questions.** "I learned that models are clever enough that impossible queries that can't be answered within the knowledge scope is answered as not enough information."

What I saw: "What is the database schema?" with `MAX_STEPS` raised to 30. The model grepped for `CREATE TABLE` / `sqlite` / `sqlalchemy`, found nothing, read 3 files to confirm, and answered "There is no database schema in this project" after 3 requests ($0.029). It still used tokens to find out: it couldn't know there was nothing until it searched. This worked because 4 small files can be fully checked; an open-ended question ("find the bug") is where an agent might keep searching, so the step cap stays. ([L2](../labs/02-agent-loop/DESIGN.md))

**Scoped tools.** "good tool implementations scopes the access permitted, raising tool errors if unauthorized access is attempted."

What I saw: asked to read `../../.env`, the model tried `read_file("../../.env")`; its thinking said "the tool itself should enforce any restriction." `source_file()` in `tools.py` resolved the path, refused it before opening anything, and the error went back as a `tool_result` with `is_error: true`. The model read the error, listed the four allowed files back, and ended with `end_turn` (2 requests, $0.008). The key never reached the model. ([L2](../labs/02-agent-loop/DESIGN.md))

**Tool names and descriptions.** "tool naming and description can matter, tho my experiment 3 didn't demonstrate that."

What I saw: changing `grep`'s description to "search stuff" gave the same path and cost as the first run (3 requests, $0.036 vs $0.035). One small change: without "regular expression (Python re syntax)" the model sent `"cost"` instead of `"(?i)cost"`. The shorter definition saved 89 input tokens on every request. The name `grep` probably carried the meaning on its own. ([L2](../labs/02-agent-loop/DESIGN.md))
### Workflows vs agents
> _prompt chaining · routing · parallelization · orchestrator–workers · evaluator–optimizer_

---

## The harness (M1–M4)

### Harness vs caller; the event stream
> _(fill after M1)_

### Coding tools & permissions
> _(fill after M2)_

### Context engineering, caching, compaction
> _(fill after M3)_

### Evals: task suites, graders, choosing model/effort with data
> _(fill after M4)_

---

## Agent capabilities (M5–M8)

### MCP, skills, server tools
> _(fill after M5)_

### Memory
> _(fill after M6)_

### Subagents
> _(fill after M7)_

### Long runs & safety
> _(fill after M8)_

---

## The platform (M9–M13)

### Sessions, transcripts, the event protocol
> _(fill after M9)_

### Where tools run (client / server / sandbox)
> _(fill after M9–M10)_

### Two clients, one backend
> _(fill after M11)_

### Identity & tenancy
> _(fill after M12)_

### Metering, billing & limits
> _(fill after M13)_

---

## Production (M14–M18)

### Deploying on AWS
> _(fill after M14)_

### Scale out & durability
> _(fill after M15)_

### Remote sandboxes
> _(fill after M16)_

### Observability
> _(fill after M17)_

### Build vs buy
> _(fill after M18)_

---

## Gotchas & insights
> _Running log of things I hit in practice, especially from "break it" experiments._

- **L1 — no output text was even produced.** With `MAX_TOKENS = 50` on a question that needed thinking, all 50 tokens went to thinking (`content blocks: ['thinking']`, `stop_reason: max_tokens`), so there was no answer at all.

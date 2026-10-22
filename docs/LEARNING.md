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
> _(fill after L2)_

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

# WORKFLOW — how each milestone runs

> The per-milestone loop. Companion: [`PLAN.md`](PLAN.md) (what's next) · [`LEARNING.md`](LEARNING.md) (what I learned) · [`DECISIONS.md`](DECISIONS.md) (why)

The principle: **build first, read second.** Concepts stick when they're attached to something I built and broke. Docs come after I've seen the thing work. When I don't know how to build something, I look up the specific docs for it right then (or ask Claude to find them), and keep building.

---

## The loop

### 1. Kickoff (5 min)
Ask Claude: *"Kick off M05"* (or *"lab 01"*). One paragraph back: what I'm building, what concept to watch for. No reading list yet.

### 2. Design (me, 20–40 min)
Copy [`templates/DESIGN.md`](templates/DESIGN.md) to `docs/design/MNN-name.md` (labs: `labs/NN-name/DESIGN.md`) and fill it in. Rough is fine — gaps are what the debate is for. Write down my *guesses* about how things work; being wrong here is where the learning comes from.

### 3. Debate (with Claude)
Prompt: *"Review my design. Challenge it: alternatives, tradeoffs, how real agent platforms do it."*
- Claude recommends; I decide.
- Cross-cutting tradeoffs → `docs/DECISIONS.md`; milestone-only ones stay in the design doc.
- I say "approved" before any code is written.

### 4. Build (Claude, in steps)
Claude implements in small steps, one concept per step, explaining the why. Through Phase 2, Claude stops after each step for review.

Everything through Phase 4 runs locally. In Phase 5, deploys go to AWS; destroy the stack when the milestone is done.

### 5. Review (me)
Read the code at the level for this milestone (below). Run it. Ask "why" about anything I couldn't have written myself.

### 6. Break it
Run the milestone's experiments from `PLAN.md`, plus any Claude suggests. Note what I saw in *Gotchas* in `LEARNING.md`.

### 7. Read
The milestone's *Read after* list. Now the essays describe something I've already touched.

### 8. Capture
- Prompt: *"Add what I learned to LEARNING.md"* — then dictate it in my words.
- Answer the *Explain it* questions out loud or in writing. Ask Claude to poke holes.
- Retro: a few lines at the bottom of the design doc — what surprised me, what I'd change.
- Run the eval suite (from M4 onward) to check nothing regressed.
- Tick the box in `PLAN.md`; move *Current step*.
- Prompt: *"Mark MNN done on the roadmap"* — Claude adds it to `DONE` in [`roadmap.html`](roadmap.html).

---

## Review levels

How closely I read the code drops as the work moves up the stack, but never to zero — and some code is always read in full.

| Where | Level | What I read |
|---|---|---|
| Labs, M1–M3 | **Every line** | All of it. If I can't explain a line, it gets rewritten or explained. |
| M4–M10, M14–M15 | **Core + tests** | The loop, protocol, tool definitions, prompts, schemas, infra stacks, tests in full; skim glue. |
| M11, M17–M18 | **Concept lines** | The design and diffs; in full only the parts carrying the new concept. |
| **Auth, billing, sandboxing** (M12, M13, M16) | **Every line, always** | Mistakes here leak data or money. |

If something surprises me at any level, I drop back to reading every line of that part.

---

## Prompts I'll reuse

- *"Kick off M05."*
- *"Review my design. Challenge it."*
- *"Approved — implement step 1."*
- *"Show me the lines that carry the concept."*
- *"Give me a break-it experiment for this."*
- *"Quiz me on M05."*
- *"Add what I learned to LEARNING.md."*
- *"Is anything in the docs stale?"*

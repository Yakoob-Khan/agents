# PLAN — what to do next

> Living doc. Roadmap + task status. Check boxes off as you go. When a level is done, prune its detail.
> Companion: [`LEARNING.md`](LEARNING.md) (concepts) · [`DECISIONS.md`](DECISIONS.md) (tradeoffs)

---

## Phase 0 — Conceptual foundations (read before code, ~4–6 hrs)

Read in order; each builds on the last.

- [ ] 1. [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — workflows vs agents; the 5 workflow patterns; the agent loop
- [ ] 2. [Anthropic cookbook — agents](https://github.com/anthropics/anthropic-cookbook) — code companion (read, don't run yet)
- [ ] 3. [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — the target architecture
- [ ] 4. [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — memory & context
- [ ] 5. [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — skim

## Phase 1 — Anthropic Academy courses ([catalog](https://anthropic.skilljar.com/))

- [ ] **Building with the Claude API** — do first; raw Messages API + tool use
- [ ] Introduction to Model Context Protocol → Advanced Topics — connecting sources
- [ ] Introduction to subagents — multi-source parallel research
- [ ] Introduction to agent skills
- [ ] *(optional)* AI Fluency for Builders

---

## Phase 2 — Build in increasing sophistication

One concept per level. Build on the raw `@anthropic-ai/sdk`. Don't build ahead of the current level. Commit at each.

| ✅ | Level | Feature | Concept |
|----|-------|---------|---------|
| [ ] | **1** | Fetch one source, summarize (single tool call) | The agent loop, tool use — by hand |
| [ ] | **2** | Multi-turn chat + conversation history | Context/message management |
| [ ] | **3** | Persistent memory across sessions | Memory & context engineering |
| [ ] | **4** | Multiple sources + routing/parallel fetch | Workflow patterns (routing, parallelization) |
| [ ] | **5** | Orchestrator + subagents per source | Multi-agent, context isolation |
| [ ] | **6** | Model switching (cheap filter → strong synthesis) | Model routing & cost |
| [ ] | **7** | Eval set + regression harness | **Evals** ← measure quality, not vibes |
| [ ] | **8** | Daily scheduled brief + observability | Productionization, MCP servers |

---

## Current step

👉 **Phase 0, item 1** — read *Building Effective Agents*. Then prompt: *"add what I learned to LEARNING.md."*

## Next up

- Decide easy sources for Level 1 (RSS / NewsAPI / public endpoints — avoid auth-gated LinkedIn/Google early)
- Scaffold TS project (Level 1 prerequisite)

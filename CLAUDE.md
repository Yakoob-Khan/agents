# CLAUDE.md — repo context for Claude

## What this is

**Briefing** is a conversational news-research agent, built as a *learning project*. The point is not just to ship an agent — it's to implement agentic concepts from scratch, in increasing sophistication, to build deep understanding (and interview-ready knowledge).

## How to work in this repo

- **Teach, don't just build.** Explain the *why* alongside code. Flag when a choice diverges from current best practice.
- **Raw Anthropic SDK first.** Do NOT reach for frameworks (LangChain, Deep Agents) until explicitly at Level 5+. Frameworks hide the loop/tool-dispatch/context mechanics that are the whole point of learning here.
- **Increasing sophistication.** Follow the Level 1–8 roadmap in `docs/PLAN.md`. Don't build ahead of the current level.
- **Small, imperative commits.** Push often.

## Doc conventions

- `docs/PLAN.md` — roadmap + task status (verbs: what to *do*). Living doc, churns.
- `docs/LEARNING.md` — concepts in the user's words (nouns: what is *true*). Append-mostly. When asked to "add what I learned," write here.
- `docs/DECISIONS.md` — tradeoff record (why X over Y).

## Stack preferences

- TypeScript, strict mode
- Const-object enums (not TS `enum`)
- Fastify over Express, Vite over Next.js for SPAs
- Raw APIs over abstractions in this learning context

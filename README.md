# Briefing

A conversational research agent that gathers news from multiple sources (AI world, tech, general) and summarizes it into a daily brief — so I don't have to visit each source myself.

**This is a learning project.** The goal is to build a real agent from the ground up on the raw Anthropic SDK, layering in agentic concepts (tool use, memory, multi-agent orchestration, model routing, evals) in increasing sophistication.

## Goals

- Chat with the agent conversationally
- Persistent memory across sessions
- Pull from multiple sources and synthesize a daily brief
- Switch models per task (cheap for filtering, strong for synthesis)
- Measure quality with evals, not vibes

## Docs

- [`docs/PLAN.md`](docs/PLAN.md) — roadmap: what to do next
- [`docs/LEARNING.md`](docs/LEARNING.md) — concepts learned
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — why choices were made

## Status

Scaffolding. See `docs/PLAN.md` for current step.

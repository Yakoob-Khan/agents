# DECISIONS — why choices were made

> Tradeoff record. Not roadmap (see [`PLAN.md`](PLAN.md)), not concepts (see [`LEARNING.md`](LEARNING.md)).
> One entry per decision. Format: context → decision → why → revisit-when.

---

## D1 — Raw Anthropic SDK over a framework (LangChain / Deep Agents)

- **Context:** Need to pick how much abstraction to build on for the agent loop, tool dispatch, and context management.
- **Decision:** Build on the raw `@anthropic-ai/sdk`. Defer frameworks until Level 5+, and adopt one then only as a deliberate comparison.
- **Why:** This is a learning project. Frameworks hide the exact mechanics (the loop, tool-call dispatch, context assembly) that are the point of learning and the thing to explain in interviews.
- **Revisit when:** At Level 5+, or if boilerplate is clearly obscuring the concept rather than teaching it.

---

## D2 — Easy sources before auth-gated ones

- **Context:** Target sources include LinkedIn, Google, CNN — some are auth-gated or have scraping/ToS constraints.
- **Decision:** Start Levels 1–4 with RSS feeds / NewsAPI / public endpoints. Treat LinkedIn-style sources as a later engineering problem.
- **Why:** Auth/ToS/scraping is an integration problem, not an agentic-concepts problem. Don't let it block the learning goal.
- **Revisit when:** Core agent works end-to-end and adding a hard source is the next real feature.

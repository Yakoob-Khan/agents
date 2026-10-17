# CLAUDE.md — repo context for Claude

## What this is

A **learning series**: the user is building an agent backend from scratch — a harness (`packages/core`) and a product server (`apps/server`) — serving two clients: a Claude Code–like coding CLI (`apps/cli`) and a Claude Desktop–like chat app (`apps/web`). Phase 1 is standalone labs (`labs/`) on the raw API.

The goal is deep, explainable understanding — not just shipped code. **Priority order:** agentic concepts first (Phases 1–3), then the platform around them (Phase 4: sessions, streaming, auth, tenancy, metering, billing), then production on AWS (Phase 5). Everything runs on the user's machine through Phase 4 (Docker Compose for Postgres/Redis). Don't pull deployment concerns earlier than Phase 5; when a local design choice will matter in production, mention it in one line and move on.

The user builds first and reads later. Don't front-load documentation; point to reading *after* the concept is visible in running code.

## The working agreement (per milestone)

Follow the loop in `docs/WORKFLOW.md`. In short:

1. **Design is the user's.** The user drafts `docs/designs/MNN-name.md` (labs: `labs/NN-name/DESIGN.md`). Don't write the design for them; ask questions, offer options.
2. **Debate before code.** Challenge the design: alternatives, tradeoffs, where it diverges from current best practice or from how production agent platforms do it. Give a recommendation, not a survey. Record settled cross-cutting tradeoffs in `docs/DECISIONS.md`.
3. **No implementation until the user approves the design.** Then implement in small, reviewable steps — one concept per step. Through Phase 2, stop after each step for review. From M4 on, run the eval suite at the end of each milestone.
4. **Teach while building.** Explain the *why* of each step. After a step, point to the specific lines that carry the concept.
5. **Suggest a "break it" experiment** for each concept so the user sees the failure mode.

## Architecture boundaries

Keep these clean; point out when a change would blur them.

- `packages/core` knows nothing about HTTP, users, or billing. It takes a config + tools, runs the loop, and emits typed events; it asks the caller for permission decisions instead of deciding.
- `apps/server` owns identity, tenancy, persistence, streaming transport, metering, and limits. It wraps core; it doesn't reimplement the loop.
- Clients speak only the event protocol. No client-specific logic in core.

## Code style for reviewability

The user reads every line in Phase 1–2 and the core of every later milestone (review levels in `docs/WORKFLOW.md`). Auth, billing, and sandboxing code are always read in full.

- Small files, explicit control flow, no clever abstractions. Prefer a plain loop the user can trace over a helper that hides it.
- Comments explain *agentic or product* reasons (why this message is appended, why this is metered here), not language syntax.
- Don't build ahead of the current milestone. If something later would help, mention it; don't add it.
- Security-sensitive defaults: tools that write files or run commands are permission-gated and scoped to a working directory from the moment they exist.

## Level rules

- Labs and core use the raw `anthropic` Python SDK. The core *is* the harness, so don't use the SDK's Tool Runner, the Claude Agent SDK, or agent frameworks inside it. They appear in M18 as a build-vs-buy comparison.
- Supporting infrastructure (DB driver, auth/crypto primitives, Stripe SDK, OpenTelemetry) is fine when a milestone's design calls for it — prefer libraries that keep the concept visible.
- Phase 5 uses AWS managed services defined in the AWS CDK (Python) under `infra/`. A managed service must not replace a concept a milestone exists to teach (e.g. auth stays hand-built; Cognito is only a comparison). Remind the user about cost: budget alarm before the first deploy, `cdk destroy` when done.

## Keep the API current

Agent APIs change fast, and recalled patterns go stale. Before writing any Claude API code, load the `claude-api` skill and check the current shapes. As of 2026-10:

- Default model `claude-opus-5-5`; `claude-sonnet-5-5` / `claude-haiku-5-5` for cheaper workers when the design calls for one. Confirm with the Models API.
- Adaptive thinking (`thinking: {type: "adaptive"}`) + `output_config.effort`, not `budget_tokens`.
- No assistant prefill and no forced `tool_choice` (`any`/`tool`) on current models; use `auto` + `strict: true` tools, or structured outputs (`output_config.format`).
- Keep conversation history **append-only**: append `response.content` whole; don't edit or reorder earlier turns. Thinking blocks and compaction depend on it.
- Always check `stop_reason` (`tool_use`, `end_turn`, `max_tokens`, `pause_turn`, `refusal`) before reading content.
- Metering must count cache reads/writes separately (`usage.cache_read_input_tokens`, `usage.cache_creation_input_tokens`); they're priced differently.

When something in these docs has gone stale, say so and propose the fix.

## Doc conventions

- `docs/PLAN.md` — roadmap + current step (verbs: what to *do*). Living doc.
- `docs/WORKFLOW.md` — the per-milestone loop and review levels.
- `docs/LEARNING.md` — concepts in the user's words (nouns: what is *true*). Append-mostly. When asked to "add what I learned," write here in the user's voice, from what they said; don't paste docs.
- `docs/DECISIONS.md` — tradeoff record (why X over Y). Format: context → decision → why → revisit-when.
- `docs/designs/MNN-name.md` — the user's milestone designs (template: `docs/designs/DESIGN.md`).
- `docs/roadmap.html` — visual roadmap. **Keep it in sync:** when a milestone is ticked in `PLAN.md`, add its code to the `DONE` list at the top of the page's script and set `UPDATED` to today's date. When milestones are added, renamed, or reordered in `PLAN.md`, update the `PHASES` data (and the system map) to match.

## Stack preferences

**Backend — Python** (labs, `packages/core`, `apps/cli`, `apps/server`, `evals/`, `infra/`):

- Type hints everywhere, checked in strict mode (checker chosen in the lab 01 design)
- Pydantic models for anything crossing a boundary (event protocol, API bodies, tool inputs)
- `asyncio` for the loop and server; FastAPI for the server
- Use the `anthropic` SDK's own types for messages and content blocks; don't redefine them

**Web client — TypeScript** (`apps/web` only):

- TypeScript, strict mode
- Const-object enums (not TS `enum`)
- Vite over Next.js for SPAs
- Protocol types generated from the Python Pydantic models, never hand-copied

**Both:** raw APIs over abstractions in this learning context.

## Git

Small, imperative commits. Commit only when the user asks.

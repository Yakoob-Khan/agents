# DECISIONS — why choices were made

> Tradeoff record. Not roadmap (see [`PLAN.md`](PLAN.md)), not concepts (see [`LEARNING.md`](LEARNING.md)).
> One entry per decision. Format: context → decision → why → revisit-when.
> Milestone-only decisions live in that milestone's design doc; cross-cutting ones go here.

---

## D1 — Build the harness on the raw Anthropic SDK

- **Context:** Options for the agent loop, tool dispatch, and context management now include the SDK's Tool Runner, the Claude Agent SDK, Claude Managed Agents, and third-party frameworks (LangGraph, Deep Agents).
- **Decision:** Labs and `packages/core` use the raw `anthropic` Python SDK. No Tool Runner, Agent SDK, or framework inside the core. Compare against them in M18.
- **Why:** The harness is the thing being learned. Using one would hide exactly the mechanics (the loop, tool dispatch, context assembly, permissions) this series is about. Comparing at the end makes build-vs-buy an informed choice.
- **Revisit when:** —

---

## D2 — ~~Easy news sources before auth-gated ones~~ (superseded)

- **Status:** Superseded by D3 — the series no longer builds a news agent.

---

## D3 — Build one agent backend serving two clients

- **Status:** Accepted.
- **Context:** The repo started as a single news agent (Briefing), then a series of separate projects. The skills I actually want: building an agent platform — the harness *and* the product concerns (auth, billing, sessions, limits) — the way Claude Code and Claude Desktop sit on a shared backend.
- **Decision:** One evolving system: `packages/core` (harness) + `apps/server` (product backend) + two clients, `apps/cli` (coding agent) and `apps/web` (chat app). Phase 1 labs stay standalone and throwaway.
- **Why:** Two very different clients force a clean harness/server/client split and a real event protocol. Product concerns (identity, metering, tenancy) only become real once there's a server with users. A coding agent also gives objective evals (tests pass or fail).
- **Tradeoff:** Later milestones carry everything earlier, so the codebase grows; review levels in `WORKFLOW.md` keep reading load manageable. Scope creep toward cloning every product feature — clone the concepts, not the polish.
- **Revisit when:** A milestone is mostly UI polish rather than agentic or product concepts — cut it.

---

## D4 — Build first, read after

- **Status:** Accepted.
- **Context:** The original plan front-loaded ~4–6 hours of reading and courses before any code.
- **Decision:** Each milestone runs design → debate → build → review → break it → read → capture (`WORKFLOW.md`). Bias toward building. When I don't know how to build something, I look up the specific docs for it at that moment; the milestone's full *Read after* list still comes after building.
- **Why:** Concepts stick better attached to something I've built and broken. Targeted lookups while building keep me unblocked without front-loading reading. Designing first (with guesses) still makes me think before Claude writes code.
- **Revisit when:** I keep making design mistakes that a short read beforehand would have prevented — then add a "read before" item for that milestone.

---

## D5 — Evals before the server, multi-agent, and model routing

- **Status:** Accepted. Evals come early so they can be rerun every time new complexity is added.
- **Context:** The original plan put evals near the end, after multi-agent and model switching.
- **Decision:** Evals are M4, right after the core works and before MCP, memory, subagents, and the server. Every later milestone runs them as a regression check. Model/effort choice is made with eval data.
- **Why:** Without evals, "subagents help" or "a cheaper model is fine" are vibes. Current guidance is to measure the strongest model at lower effort before building a multi-model cascade, which needs an eval to test.
- **Revisit when:** —

---

## D6 — Monorepo with workspaces; labs stay standalone

- **Status:** Accepted: all the code in one repo. Supersedes the earlier "copy forward, no shared library" idea.
- **Context:** Core, server, and two clients share types (especially the event protocol) and must evolve together.
- **Decision:** One repo. The Python packages (`packages/core`, `apps/cli`, `apps/server`, `evals/`, `infra/`) form one workspace (e.g. a `uv` workspace); `apps/web` is a separate TypeScript package. The event protocol is defined once as Pydantic models in Python; the web client's types are generated from their JSON Schema. `labs/` are separate, throwaway packages. Tooling decided in the lab 01 and M1 designs.
- **Why:** The boundaries between packages are part of what's being learned; a monorepo makes them explicit and checked by the type checker. Generating the TS types keeps the cross-language protocol from drifting.
- **Revisit when:** —

---

## D7 — The CLI starts as a local agent, then becomes a client of the server

- **Status:** Accepted. Build a local agent first, designed so it can later run remotely.
- **Context:** Claude Code runs its loop locally; a Claude Code clone could too. But the goal is a backend that serves both clients and owns auth, metering, and limits.
- **Decision:** Through Phase 3 (M1–M8), the CLI runs `packages/core` in-process: a working local coding agent. In M10 it switches to talking to `apps/server`.
- **Why:** The agentic concepts come first and are easiest to see without a network in the way. Routing the CLI through the server later is what makes identity, metering, and sessions real for it, and it raises the question in D8. Having built both shapes, I can explain the tradeoff.
- **Tradeoff:** Extra latency and a harder design than a purely local agent. It also differs from how Claude Code actually works, which is worth being able to explain.
- **Revisit when:** M10 design, if the tool-execution split (D8) proves unworkable.

---

## D8 — Where tools execute (open — decide in M9)

- **Status:** Open.
- **Context:** The coding CLI needs to touch files on the user's machine; the web client has no local machine. Options: (a) the server runs the loop and asks the CLI to execute tools locally; (b) the loop runs locally in the CLI and the server only proxies model calls, meters, and stores transcripts; (c) everything runs in a server-side sandbox (M16).
- **Decision:** _Decide in the M9 design._ Deliberately left open: building the agent in Phases 2–3 will give me the understanding to answer it.
- **Revisit when:** M16.

---

## D9 — Local first; deployment last

- **Status:** Accepted.
- **Context:** The series covers agentic concepts, the platform, and production infrastructure. Deploying early would spread attention across cloud concerns before the agent works.
- **Decision:** Phases 1–4 run entirely on my machine (Docker Compose for Postgres and Redis from M9). AWS appears only in Phase 5 (M14–M18), once the system works end to end locally.
- **Why:** Agentic concepts are the priority. Seeing the finished system then work and break in production is a better infra lesson than deploying a half-built one, and it avoids paying for cloud resources during months of local work.
- **Tradeoff:** Some local choices (e.g. in-memory state, sticky streams) will need rework when scaling out in M15. That rework is itself part of the lesson. Flag such choices briefly when they're made.
- **Revisit when:** —

---

## D10 — AWS managed services, defined with CDK

- **Status:** Accepted for now; revisit in the M14 design. Model calls go through the Anthropic SDK against the Anthropic API, also when deployed on AWS.
- **Context:** Phase 5 needs a cloud. The goal is learning to deploy and operate an agent platform on infra services, not to build infrastructure from scratch.
- **Decision:** AWS managed services (ECS Fargate, ALB, RDS Postgres, ElastiCache, SQS, S3, Secrets Manager, CloudWatch), defined in the AWS CDK in Python; CI/CD via GitHub Actions with OIDC. Keep calling the Anthropic API directly rather than through Bedrock.
- **Why:** Managed services are how real agent platforms run, and the lessons are in how agent workloads strain their defaults (ALB idle timeouts vs long streams, SQS visibility timeouts vs long runs). CDK keeps everything in one language. The direct API keeps the core unchanged and gives every API feature.
- **Tradeoff:** CDK is AWS-only and hides CloudFormation; Terraform would be more portable. CDK's own tooling still needs Node installed, even with Python stacks. Cost: always-on resources (NAT, ALB, RDS, ElastiCache) add up, so set a budget alarm and destroy stacks between milestones.
- **Revisit when:** M14 design.

---

## D11 — Python for the backend; TypeScript only for the web client

- **Status:** Accepted.
- **Context:** The series was planned in TypeScript. The agent backend is the focus, and Python is the most common language for agent and AI backend work.
- **Decision:** Python for labs, `packages/core`, `apps/cli`, `apps/server` (FastAPI), `evals/`, and `infra/` (CDK). TypeScript only for `apps/web`, the browser client.
- **Why:** Python is where most agent tooling, examples, and production agent backends live. The CLI must be Python because it runs core in-process through Phase 3 (D7). The web client stays TypeScript because it runs in a browser. The cross-language boundary also makes the event protocol a real contract.
- **Tradeoff:** Two languages in one repo, and the protocol needs schema generation (D6). Python needs a type checker in strict mode to get the safety TypeScript gives by default.
- **Revisit when:** —

---

## D12 — Python tooling: uv, Ruff, mypy, pytest on Python 3.12

- **Status:** Accepted (lab 01 design). Carries forward to every Python package in the repo.
- **Context:** The backend is Python (D11) and needs a package manager, linter/formatter, type checker, and test runner.
- **Decision:** Python 3.12; `uv` for dependencies, virtual environments, and Python versions; Ruff for linting and formatting; mypy in strict mode for type checking; pytest for tests.
- **Why:** The most common industry combination. `uv` and Ruff are the current standards (both from Astral); mypy is the most widely used checker in industry codebases and CI; pytest is the standard test runner.
- **Tradeoff:** pyright would match the errors shown in Cursor's editor; newer checkers (ty, Pyrefly) are faster but less established. Python 3.14 is the current stable release; 3.12 is still supported.
- **Revisit when:** A dependency needs a newer Python, or mypy gets in the way of learning.

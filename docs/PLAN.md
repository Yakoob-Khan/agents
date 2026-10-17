# PLAN — what to do next

> Living doc. Roadmap + current step. Tick boxes as you go; prune a milestone's detail once it's done.
> Visual version with progress: [`roadmap.html`](roadmap.html) (open in a browser) · How each milestone runs: [`WORKFLOW.md`](WORKFLOW.md) · Companion: [`LEARNING.md`](LEARNING.md) (concepts) · [`DECISIONS.md`](DECISIONS.md) (tradeoffs)

**Order of priority:** agentic concepts first, then the platform around them, then production. Everything through Phase 4 runs on my own computer (Docker Compose for Postgres/Redis when needed). AWS comes only in Phase 5, once the system works locally (D9).

---

## Current step

👉 **Lab 01 — kickoff.** Prompt: *"Kick off lab 01."* Then copy `docs/designs/DESIGN.md` to `labs/01-messages/DESIGN.md` and draft it.

Decide in the lab 01 design (they carry forward): Python version, package manager (e.g. `uv`), linter/formatter (e.g. `ruff`), type checker (`mypy` or `pyright`, strict), test runner (`pytest`), how the API key is supplied.

---

## Overview

| ✅ | # | Milestone | Concepts | Review |
|---|---|---|---|---|
| | | **Phase 1 — Labs** (`labs/`, standalone) | | |
| [ ] | L1 | `messages` | Messages API, tokens, streaming, thinking/effort, structured output | Every line |
| [ ] | L2 | `agent-loop` | The loop and tool use, by hand | Every line |
| [ ] | L3 | `workflows` | Workflows vs agents, the five patterns | Every line |
| | | **Phase 2 — The harness** (`packages/core` + local CLI) | | |
| [ ] | M1 | Harness + local coding CLI | Loop as a library, event stream, cancellation | Every line |
| [ ] | M2 | Coding tools + permissions | Read/Edit/Write/Bash/Glob/Grep, permission modes | Every line |
| [ ] | M3 | Context management | Prompt assembly, caching, compaction, project instructions | Every line |
| [ ] | M4 | Evals | Task suites, graders, model/effort choice, transcript inspection | Core + tests |
| | | **Phase 3 — Agent capabilities** (still local) | | |
| [ ] | M5 | Extensibility | MCP, skills, server tools, tool search | Core + tests |
| [ ] | M6 | Memory | Memory tool, what to remember, poisoned memory | Core + tests |
| [ ] | M7 | Subagents | Orchestrator–workers, context isolation, parallelism | Core + tests |
| [ ] | M8 | Long runs & safety | Prompt injection, permission policies, refusals, task budgets, local sandbox | Core + tests |
| | | **Phase 4 — The platform** (local: server + two clients) | | |
| [ ] | M9 | Server & sessions | Event protocol, persistence, resume, where tools run | Core + tests |
| [ ] | M10 | CLI as a client | Remote loop, client-executed tools, approvals over the wire | Core + tests |
| [ ] | M11 | Web client | Second client, streaming UI, uploads, projects | Concept lines |
| [ ] | M12 | Identity & tenancy | Users, orgs, API keys, CLI login, web sessions, authorization | **Every line** |
| [ ] | M13 | Metering, billing & limits | Usage ledger, pricing, credits, Stripe, quotas, rate limits | **Every line** |
| | | **Phase 5 — Production on AWS** | | |
| [ ] | M14 | Deploy | CDK, Fargate, ALB, RDS, Secrets Manager, CI/CD, budgets | Core + tests |
| [ ] | M15 | Scale out & durability | SQS workers, Redis pub/sub, crash recovery, draining, load tests | Core + tests |
| [ ] | M16 | Remote sandboxes & background tasks | Sandbox per session, egress control, long-running jobs | **Every line** |
| [ ] | M17 | Observability & operations | OpenTelemetry, CloudWatch, SLOs, cost per task | Concept lines |
| [ ] | M18 | Build vs buy | Compare my core to Agent SDK, Managed Agents, a framework | Concept lines |

Each milestone lists: **Build** (rough scope; my design decides the details), **Concepts**, **Break it**, **Read after**, **Explain it**.

---

## Phase 1 — Labs

Throwaway, small programs on the raw API. The point is to see the mechanics before wrapping them in a library.

### L1 · `messages`
- **Build:** a CLI that sends a prompt (e.g. "explain this file") and prints the answer. Then: stream it; print token usage and cost; return structured JSON.
- **Concepts:** request/response shape (`messages`, `system`, roles, content blocks), `stop_reason`, `usage` and pricing, streaming, adaptive thinking and `effort`, structured outputs.
- **Break it:** tiny `max_tokens` → `stop_reason: "max_tokens"`; same prompt at `low` vs `high` effort (tokens, latency, quality).
- **Read after:** [streaming](https://platform.claude.com/docs/en/build-with-claude/streaming), [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking), [effort](https://platform.claude.com/docs/en/build-with-claude/effort), [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs), [pricing](https://platform.claude.com/docs/en/about-claude/pricing).
- **Explain it:** What's sent on each request? What decides when the model stops? How do I compute what a request cost?

### L2 · `agent-loop`
- **Build:** a hand-written loop with **read-only** tools (`list_files`, `read_file`, `grep`) over a sample repo. Ask "how does auth work in this repo?" and let Claude explore.
- **Concepts:** tool definitions and descriptions, `tool_use` / `tool_result`, `while stop_reason == "tool_use"`, parallel tool calls (all results in one user message), `is_error`, `strict: true`, iteration limits.
- **Break it:** vague tool description; tool returns an error; a 50k-token tool result; split parallel results across two messages; no iteration cap + impossible task.
- **Read after:** [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), [tool use overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview), [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents).
- **Explain it:** Draw the loop. Who executes the tool? What makes a tool description good?

### L3 · `workflows`
- **Build:** a "review this diff" task done as code-controlled workflows (chaining, routing, parallelization, evaluator–optimizer), then the same task as an L2-style agent. Compare.
- **Concepts:** workflows vs agents; the five patterns; determinism, cost, latency.
- **Break it:** an input the fixed workflow didn't anticipate; tokens and wall-clock, workflow vs agent.
- **Read after:** [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (workflow half).
- **Explain it:** When would a product use a workflow instead of an agent?

## Phase 2 — The harness

`packages/core` is the agent; `apps/cli` drives it **in-process** as a local coding agent (Claude Code–like). By the end of this phase I have a working coding agent on my machine.

### M1 · Harness + local coding CLI
- **Build:** move the L2 loop into a library emitting a **typed event stream** (text deltas, thinking, tool call started/finished, turn complete, error, done). Tool registry. Cancellation (abort mid-stream and mid-tool). A terminal CLI that consumes the events.
- **Concepts:** the harness as a separable component; events as the contract with callers; interruption.
- **Break it:** cancel mid tool call and inspect the transcript; throw inside a tool.
- **Read after:** [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).
- **Explain it:** What's the harness responsible for, and what's the caller responsible for? Why an event stream?

### M2 · Coding tools + permissions
- **Build:** Read, Write, Edit (string replace), Bash, Glob, Grep, scoped to a working directory. Permission modes (ask / read-only / allow-all) where the harness emits a *permission request event* and waits for the caller's answer; the CLI prompts me.
- **Concepts:** bash vs dedicated tools; tool result size limits; permission as a protocol, not a prompt; least privilege.
- **Break it:** ask for `rm -rf` outside the working dir; path traversal (`../../`); an Edit whose `old_string` isn't unique; a command that never exits.
- **Read after:** [Bash tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool), [text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool), [Beyond permission prompts](https://www.anthropic.com/engineering/claude-code-sandboxing).
- **Explain it:** Why does Claude Code have both Bash *and* Grep/Read? How would I stop the agent damaging my machine?

### M3 · Context management
- **Build:** system prompt assembly (base prompt + environment info + a project instructions file à la `CLAUDE.md`); prompt caching with deliberate breakpoints; token accounting per turn; context editing and server-side compaction for long sessions; append-only transcript saved to disk; `/compact` and `/resume` in the CLI.
- **Concepts:** context as a budget; cache prefix stability; clearing vs compacting; why history is append-only.
- **Break it:** put a timestamp in the system prompt and watch cache reads drop to zero; a long session with and without compaction; edit an earlier turn.
- **Read after:** [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing), [compaction](https://platform.claude.com/docs/en/build-with-claude/compaction).
- **Explain it:** What goes in the context and in what order, and why? What does caching save, and what breaks it?

### M4 · Evals
- **Build:** a suite of small coding tasks in fixture repos, graded by running tests plus an LLM rubric for what tests miss. A runner reporting pass rate, tokens, cost, and time per task, and a way to read a failed run's transcript. Use it to choose model and effort, and as a regression check for every later milestone.
- **Concepts:** task suites, graders (code / model / human), noise and repeat runs, cost per *completed* task; measure one strong model at lower effort before building a model cascade.
- **Break it:** change one word in the system prompt and see if the eval catches it; run twice and measure noise.
- **Read after:** [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), [Quantifying infrastructure noise](https://www.anthropic.com/engineering/infrastructure-noise), [cost and intelligence tradeoffs](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence).
- **Explain it:** How do I know a change made the agent better? Why test-based graders for a coding agent?

## Phase 3 — Agent capabilities

Still the local CLI. Each milestone adds a capability to core and measures it with the M4 evals.

### M5 · Extensibility: MCP, skills, server tools
- **Build:** an MCP client in core (connect local stdio servers); write one small MCP server myself; skills (instructions + scripts loaded on demand); server tools (`web_search`, `web_fetch`); tool search when tools pile up.
- **Concepts:** MCP's host/client/server split; progressive disclosure; tool definitions as context cost; client vs server tools.
- **Break it:** connect 40 tools and measure selection quality and tokens; an MCP tool with a malicious description.
- **Read after:** [MCP docs](https://modelcontextprotocol.io), [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp), [Introducing advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use), [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills).
- **Explain it:** MCP vs skills vs plain tools: when is each the right fit?

### M6 · Memory
- **Build:** persistent memory across sessions via the memory tool, backed by files I control; compare with plain project instructions (M3).
- **Concepts:** memory vs context; who decides what's remembered; retrieval vs always-loaded; stale and poisoned memory.
- **Break it:** tell it a false preference and watch it persist; plant an instruction in a file the agent reads and see if it reaches memory.
- **Read after:** [memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool).
- **Explain it:** What are the risks of model-written memory? How is memory different from a bigger context window?

### M7 · Subagents
- **Build:** a Task-style tool that spawns a subagent with its own context, tool subset, and model (cheaper workers); parallel subagents; condensed results back to the lead.
- **Concepts:** orchestrator–workers, context isolation, delegation prompts, the token cost of multi-agent.
- **Break it:** vague delegation; subagents returning raw dumps; compare quality and tokens against a single agent on the M4 eval.
- **Read after:** [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system), [Building a C compiler with parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler).
- **Explain it:** When is multi-agent worth its cost?

### M8 · Long runs & safety
- **Build:** prompt-injection defenses for tool output (files, fetched pages, MCP results); permission policies (allow/ask/deny rules); `refusal` handling and fallbacks; task budgets and progress checkpoints for long tasks; optionally run Bash inside a local Docker container.
- **Concepts:** trust boundaries; untrusted content in the context; long-horizon agents; containment.
- **Break it:** red-team it: plant instructions in a file or web page; give it a task that runs past its budget.
- **Read after:** [How we built Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode), [How we contain Claude across products](https://www.anthropic.com/engineering/how-we-contain-claude), [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps).
- **Explain it:** What's the threat model of an agent that reads files and the web and runs code?

## Phase 4 — The platform

Still local: the server, Postgres, and Redis run on my machine (Docker Compose).

### M9 · Server & sessions
- **Build:** a FastAPI server wrapping core: create session, send message, stream events, cancel, resume. Postgres for sessions and transcripts (append-only event log). A versioned, ordered **event protocol** a client can resume after a dropped connection.
- **Concepts:** where the loop runs; transcripts as durable state; what happens to a running turn when the client disconnects.
- **Decide (D8):** where tools execute: client machine, server, or sandbox.
- **Break it:** kill the client mid-turn and reconnect; send the same message twice; restart the server mid-session.
- **Read after:** [Server-sent events (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events), [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents).
- **Explain it:** Walk through one user message from client to model and back. What survives a disconnect?

### M10 · CLI as a client
- **Build:** switch the CLI from in-process core to the server (D7): streaming, approvals over the wire, slash commands, and (per D8) executing file/bash tools locally on behalf of the server.
- **Concepts:** client-executed tools; a network round trip per tool call; trusting the client.
- **Break it:** deny a permission; go offline during a tool call.
- **Read after:** [Claude Code docs](https://code.claude.com/docs/en/overview); compare features with mine.
- **Explain it:** Why might the loop run on a server while tools run on my laptop? What's the security model?

### M11 · Web client (Claude Desktop–like)
- **Build:** a TypeScript Vite SPA on the same event protocol (types generated from the Python models): conversation list, streaming rendering (markdown, thinking, tool calls), approval UI, file uploads, projects (shared instructions + files across conversations).
- **Concepts:** showing an agent's work so a human can follow and steer it.
- **Break it:** open the same session in two tabs; refresh mid-stream.
- **Read after:** [Files API](https://platform.claude.com/docs/en/build-with-claude/files).
- **Explain it:** What had to change in the protocol for a second client, and what didn't?

### M12 · Identity & tenancy
- **Build:** users and organizations; API keys (hashed at rest); CLI login via OAuth device flow; cookie sessions for the web; authorization on every session access; per-user MCP connector credentials.
- **Concepts:** authn vs authz, key hashing and rotation, device flow, CSRF, tenant isolation.
- **Break it:** read another user's session by guessing an ID; reuse a revoked key; replay a device code.
- **Read after:** [RFC 8628 (OAuth device authorization grant)](https://datatracker.ietf.org/doc/html/rfc8628), [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html).
- **Explain it:** How does a CLI login probably work? How is one org's data kept from another's?

### M13 · Metering, billing & limits
- **Build:** a usage ledger from every model call (input, output, cache read, cache write, per model), priced into cost and attributed to session, user, and org (including subagents); credits or plans; Stripe in test mode; quotas and rate limits (token bucket in Redis); per-session budgets; handling upstream 429s.
- **Concepts:** one agent turn = many model calls; idempotent usage events; metering vs billing; rate-limit algorithms.
- **Break it:** a looping agent with no budget; double-count a retried request; two concurrent sessions hitting the upstream rate limit.
- **Read after:** [Stripe usage-based billing](https://docs.stripe.com/billing/subscriptions/usage-based), [Claude rate limits](https://platform.claude.com/docs/en/api/rate-limits).
- **Explain it:** Where does a turn's cost come from, and how do I stop one from costing $50?

## Phase 5 — Production on AWS

Managed AWS services, defined with the AWS CDK in Python (D10). Before the first deploy: an **AWS Budgets alarm**. Tear the stack down (`cdk destroy`) between milestones.

### M14 · Deploy
- **Build:** containerize server and web; a CDK stack with VPC, ECS Fargate behind an ALB, RDS Postgres, Secrets Manager, S3; CI/CD from GitHub Actions using OIDC (no stored AWS keys). Point the CLI at it.
- **Concepts:** infrastructure as code; networking basics (public/private subnets, security groups); long-lived streams vs load balancer idle timeouts.
- **Break it:** a stream idle longer than the ALB timeout; a deploy while a session is mid-turn.
- **Read after:** [AWS CDK developer guide](https://docs.aws.amazon.com/cdk/v2/guide/home.html), [ALB idle timeout](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/application-load-balancers.html#connection-idle-timeout).
- **Explain it:** Trace a request from my laptop to the model and back through every AWS component.

### M15 · Scale out & durability
- **Build:** separate agent workers from API servers via SQS; multiple instances with streams fanned out through ElastiCache (Redis) pub/sub; crash recovery from the event log; graceful draining on deploy; load tests against a **mock model server** (no API bill).
- **Concepts:** stateless API + stateful runs; at-least-once delivery and idempotent tool calls; SQS visibility timeout vs a 20-minute agent run; durable execution (own checkpoints vs Step Functions).
- **Break it:** kill a worker mid-run; reconnect a client to a different instance; flood the queue.
- **Read after:** [SQS visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html).
- **Explain it:** What happens to an agent run when the machine running it dies?

### M16 · Remote sandboxes & background tasks
- **Build:** run coding sessions in a sandbox per session (a Fargate task with a cloned repo) so the web client can run coding tasks; egress restricted by network policy; secrets kept out of the sandbox; background tasks with completion notifications.
- **Concepts:** "brain vs hands" in production; isolation, cold starts, egress control.
- **Break it:** a task that tries to exfiltrate an env var or reach an internal service; a sandbox that never finishes.
- **Explain it:** What does a hosted coding agent need that a local one doesn't?

### M17 · Observability & operations
- **Build:** OpenTelemetry traces per turn (model calls, tool calls, subagents) into CloudWatch/X-Ray; cost-per-task dashboards; alarms; logs that don't leak user content; autoscaling on queue depth.
- **Concepts:** debugging nondeterministic systems from traces; SLOs for agents (what's "available" for a 10-minute task?).
- **Read after:** [OpenTelemetry for Claude](https://platform.claude.com/docs/en/manage-claude/opentelemetry).
- **Explain it:** A user says "the agent got stuck." How do I find out why?

### M18 · Build vs buy
- **Build:** reimplement one slice with the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk), with [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview), and optionally a framework (e.g. LangGraph). Compare control, code size, cost, lock-in, and what each gives for free. Optionally compare my M12 auth with Cognito.
- **Explain it:** If I were starting a real agent product tomorrow, what would I build and what would I buy?

---

## Optional, alongside

- [Anthropic engineering blog](https://www.anthropic.com/engineering): check for new posts at each phase boundary.
- [Claude cookbooks](https://github.com/anthropics/claude-cookbooks): compare implementations after building.
- [Anthropic Academy](https://anthropic.skilljar.com/) courses, if I want a structured walkthrough after a milestone.

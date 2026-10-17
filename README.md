# agents

A hands-on learning series: building an **agent backend** from scratch (the harness *and* the platform around it) that serves two clients:

- a **coding-agent CLI** (Claude Code–like): works in a local repo, reads/edits files, runs commands, asks permission;
- a **chat app** (Claude Desktop–like): conversations, file uploads, connectors, memory, projects.

**Priorities, in order:** agentic concepts (the loop, tools, context, evals, MCP, memory, subagents, safety) → the platform (sessions, streaming, auth, multi-tenancy, metering, billing) → production on AWS. Everything runs on my own computer until the final phase.

**Build first, read second.** I design each milestone and debate it with Claude, Claude Code implements it, I read the code and break it on purpose, and only *then* read the docs and essays behind it.

## Architecture (target)

```
   apps/cli  (coding agent)            apps/web  (chat app)
   terminal UI · local tool exec       Vite SPA · approvals · uploads
              │                                │
              └──────── HTTP + event stream ───┘
                              │
                    apps/server  (FastAPI)
   auth · orgs · sessions · streaming · metering · billing · rate limits
                              │
                    packages/core  (the harness)
   agent loop · tools · permissions · context · subagents · MCP · skills
                              │
          Anthropic API · Postgres · Redis · sandboxes · object storage
```

The harness doesn't know about HTTP or users; the server doesn't know how the loop works; the clients only speak the event protocol. Until Phase 4, the CLI runs the harness in-process as a local coding agent.

## Phases

| Phase | Milestones | Runs |
|---|---|---|
| 1. Labs | L1–L3: raw API, the loop by hand, workflows vs agents | Local |
| 2. The harness | M1–M4: core library + coding CLI, tools & permissions, context, evals | Local |
| 3. Agent capabilities | M5–M8: MCP & skills, memory, subagents, long runs & safety | Local |
| 4. The platform | M9–M13: server & sessions, CLI as client, web client, identity, metering & billing | Local (Docker Compose) |
| 5. Production | M14–M18: deploy, scale out, remote sandboxes, observability, build vs buy | AWS |

Roadmap and current step: [`docs/PLAN.md`](docs/PLAN.md), or the visual version with progress, [`docs/roadmap.html`](docs/roadmap.html). How each milestone runs: [`docs/WORKFLOW.md`](docs/WORKFLOW.md).

## Repo layout

```
agents/
├── CLAUDE.md              # how Claude works in this repo
├── labs/NN-name/          # Phase 1: standalone, one concept each
├── packages/core/         # the harness (from Phase 2)
├── apps/
│   ├── cli/               # coding-agent client (from Phase 2)
│   ├── server/            # FastAPI backend (from Phase 4)
│   └── web/               # chat client (from Phase 4)
├── evals/                 # eval suites + runner (from M4)
├── infra/                 # AWS CDK stacks (Phase 5)
└── docs/
    ├── PLAN.md            # roadmap + current step
    ├── roadmap.html       # visual roadmap with progress (open in a browser)
    ├── WORKFLOW.md        # the per-milestone loop
    ├── LEARNING.md        # concepts in my own words
    ├── DECISIONS.md       # tradeoffs (why X over Y)
    ├── design/            # one design doc per milestone
    └── templates/DESIGN.md
```

## Stack

**Python** for everything backend: labs, the harness, the CLI, the server, evals, and infra. Raw [`anthropic`](https://github.com/anthropics/anthropic-sdk-python) SDK: the harness *is* the thing being built, so no agent frameworks; they appear only in the final build-vs-buy comparison. FastAPI for the server, Postgres and Redis via Docker Compose locally, AWS managed services (via CDK in Python) in Phase 5.

**TypeScript** only for the web client (Vite SPA), with protocol types generated from the Python models.

## Status

Not started. See [`docs/PLAN.md`](docs/PLAN.md) → *Current step*.

# Letta Code — The Memory-First Coding Agent

**Letta Code** is a CLI coding agent that gives you a persistent, model-portable collaborator with git-backed memory, skills, and subagents. Think of it as Claude Code / Codex / Cursor-CLI with a persistent brain that survives model swaps, sessions, and project switches.

Upstream: [github.com/letta-ai/letta-code](https://github.com/letta-ai/letta-code)
Blog intro: [letta.com/blog/letta-code](https://www.letta.com/blog/letta-code)
App intro: [letta.com/blog/introducing-the-letta-code-app](https://www.letta.com/blog/introducing-the-letta-code-app)
Docs: [docs.letta.com/letta-code/](https://docs.letta.com/letta-code/)

---

## Why Letta Code (vs Claude Code / Codex / Cursor CLI)

Every other coding-agent CLI is stateless — each session starts cold. Letta Code keeps a **persistent Letta agent** underneath the CLI. That agent:

- Has core memory blocks, archival memory, and conversation recall — **across sessions**
- Can be **model-swapped** mid-session (Claude → GPT → Gemini → Kimi) without losing context
- Learns **skills** from trajectories via `/skill`
- Spawns **subagents** for scoped work without polluting the parent's memory
- Stores its memory **git-backed** — your agent's knowledge is versioned alongside your code

If Clay is doing serious agentic coding work, this is the meta-tool.

---

## Installation

```sh
npm install -g @letta-ai/letta-code
letta-code --version
```

First run prompts for:
- A **Letta API key** (for the backing agent and persistent memory)
- A **model provider key** (Anthropic, OpenAI, Google, Z.AI/GLM, Moonshot/Kimi) — the model the agent will use *inside* the CLI
- A **working directory** (where git-backed memory lives)

## Running

```sh
cd /path/to/project
letta-code
```

This opens an interactive REPL. The agent has the working directory as its context and can read/write files, run shell commands, spawn subagents, call tools, and — critically — **remember everything across invocations**.

---

## Key Commands

| Command | What it does |
|---|---|
| `/remember <note>` | Explicitly push a note into the agent's core memory. Use for commitments, constraints, preferences you want it to carry forward. |
| `/skill <name>` | Ask the agent to learn a skill from the current trajectory. Packages the last N messages + outcomes as a reusable skill. |
| `/subagent <prompt>` | Spawn a scoped subagent for this task only. Returns when done; subagent memory does not pollute the parent. |
| `/memory` | Inspect current core memory blocks. |
| `/model <model-id>` | Switch the backing model. Memory and identity persist. |
| `/provider <name>` | Switch provider (anthropic / openai / google / moonshot / z-ai). |
| `/export` | Export the agent (as `.af` — "agent file") for portability or backup. |
| `/session` | List, switch between, or create named sessions. |
| `/help` | Full command list. |

(Command set may expand; check `letta-code --help` or `/help` for current surface.)

---

## Supported Models

Letta Code is **model-portable by design**. Supported model families include:

- **Anthropic**: `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `o1`, Codex models
- **Google**: `gemini-2.0-flash`, `gemini-1.5-pro`
- **Z.AI (GLM)**: GLM-4 family
- **Moonshot (Kimi)**: Kimi-K2.5

**Important constraint:** the "no Anthropic on Letta Cloud" rule applies to agents whose **model is routed by Letta Cloud itself**. Letta Code is different — it uses *your* provider keys directly, so Claude works there. You can use Claude in Letta Code even if Clay's other Letta-hosted agents can't.

---

## Mental Model: Letta Code = CLI Wrapper + Persistent Letta Agent

The CLI is a thin wrapper. The real substance is the Letta agent it's bound to. That agent lives in Letta Cloud (or self-hosted) and can be inspected/managed the same way any other Letta agent can — via the Python/TS SDKs, via the REST API, via this skill's other references.

**Implication:** you can drive Letta Code from outside. You can:

- Push memory blocks programmatically via the API → the CLI agent sees them on next invocation
- Share memory blocks between the Letta Code agent and your Paperclip/Doer agents via shared blocks
- Inspect what skills the agent has learned
- Export/import the agent between machines

This is **Letta Code's superpower** — it's not a silo like other coding CLIs. It's a first-class Letta agent that happens to have a great terminal UI.

---

## Git-Backed Memory

Letta Code stores memory artifacts in a versioned directory alongside your code. The exact layout varies by version but typically includes:

- `.letta/` in your working directory
- `.letta/memory/` — serialized memory block snapshots
- `.letta/skills/` — learned skills (one dir per skill)
- `.letta/subagents/` — subagent definitions
- `.letta/sessions/` — session logs

Commit `.letta/` to git if you want the agent's knowledge to be portable across clones. Add specific subdirs to `.gitignore` if you want ephemeral scratch (e.g., session logs) to stay local.

---

## Skills in Letta Code vs Skills in Claude Code

Both have a concept of "skills," but they differ:

| | Claude Code / Anthropic Skills | Letta Code |
|---|---|---|
| Authoring | Hand-crafted markdown + optional scripts | Learned from trajectory via `/skill` |
| Storage | File system, static | Git-backed memory, evolves |
| Scope | Global to the agent that has the skill | Per-Letta-agent; can be shared via blocks |
| Invocation | Triggered by description match | Can be triggered explicitly or via agent judgment |
| Portability | `.skill` files | `.af` (agent file) export includes learned skills |

Both work. Letta Code's advantage is that skills can be **learned in place** from successful runs. Claude Code's advantage is that skills are **human-curated** and testable offline.

---

## Subagents in Letta Code

`/subagent <prompt>` spawns a fresh Letta agent scoped to this task. The subagent:

- Inherits a subset of the parent's context (the spawn prompt)
- Gets its own memory, tools, and session
- Does not pollute the parent's memory
- Returns a final summary to the parent when done

Use subagents for:
- **Scoped exploration** — "go learn this codebase" without the parent agent mixing that context with its main task
- **Parallel work** — multiple subagents run concurrently on independent subtasks
- **Safety isolation** — experimental or destructive operations that shouldn't touch the parent's state

---

## Model Swap Mid-Session

The killer feature. Example workflow:

```
> /model claude-opus-4-6
Switched to claude-opus-4-6. Memory intact.

> Help me refactor this module...
[... Opus thinks hard, produces plan ...]

> /model gpt-4o-mini
Switched to gpt-4o-mini. Memory intact.

> Now execute the plan.
[... cheaper model executes the plan step by step ...]

> /model kimi-k2.5
Switched to kimi-k2.5. Memory intact.

> Summarize what was done.
[... Kimi summarizes with full context ...]
```

Planner/executor split using three different models, one agent. This is a real competitive advantage for cost/quality optimization.

---

## Driving Letta Code from the API

Because Letta Code is just a CLI wrapped around a Letta agent, you can influence it from outside:

**Push a memory update from your dev tools into the agent:**

```python
from letta_client import Letta
import os

client = Letta(token=os.environ["LETTA_API_KEY"])
letta_code_agent_id = "agent-your-letta-code-agent-id"  # find via client.agents.list()

client.agents.blocks.modify(
    agent_id=letta_code_agent_id,
    block_label="current_project_context",
    value="Working on donjon-paperclip plugin-wiki-graph. Focus on Phase 2 memfs integration.",
)
```

Next time you open `letta-code` in that project, the agent has this context already loaded.

**Inspect what the CLI agent has learned:**

```python
blocks = client.agents.blocks.list(agent_id=letta_code_agent_id)
for b in blocks:
    print(b.label, len(b.value), b.description)
```

---

## Workflow: Finding Your Letta Code Agent

The Letta Code CLI creates a persistent agent on first run. To find it via the API:

```python
agents = client.agents.list()
letta_code_agents = [a for a in agents if "letta-code" in (a.tags or []) or "letta-code" in a.name.lower()]
```

The exact tagging convention depends on the Letta Code version. Typically one per project or one global.

---

## Workflow: Export / Import Your Agent

Export your Letta Code agent to a portable `.af` file:

```python
from letta_client import Letta
client = Letta(token=os.environ["LETTA_API_KEY"])

exported = client.agents.export(agent_id=letta_code_agent_id)
with open("letta-code-agent-backup.af", "w") as f:
    f.write(exported)
```

Import on another machine / account:

```python
with open("letta-code-agent-backup.af") as f:
    new_agent = client.agents.import_agent(body=f.read())
```

This is how you move your learned agent between laptops, between Letta Cloud accounts, or between self-hosted and cloud.

---

## Common Letta Code Asks

### "Install and configure Letta Code for my project"

```sh
npm install -g @letta-ai/letta-code
cd /path/to/project
letta-code
# paste LETTA_API_KEY when prompted
# paste your model provider key (e.g. ANTHROPIC_API_KEY) when prompted
```

Add `.letta/sessions/` to `.gitignore` (ephemeral logs). Commit `.letta/memory/` and `.letta/skills/` if you want portability.

### "Teach Letta Code a new skill from what it just did"

At the end of a successful run:

```
> /skill <skill-name>
```

The agent packages recent trajectory as a reusable skill. Next time you use the same pattern, it can invoke the learned skill.

### "Swap the model for this task"

```
> /model claude-sonnet-4-6
```

Memory stays. Just the model changes.

### "Push a constraint into memory for the rest of the session"

```
> /remember Don't modify files under packages/db/ — migration is pending
```

The agent holds this in core memory for future steps.

### "Start a fresh subagent for exploration"

```
> /subagent Learn the shape of packages/plugins/examples/plugin-wiki-graph/ and report back the main entry points
```

The subagent does the work and returns a summary. Parent's memory is untouched.

---

## When Letta Code Is Not the Right Tool

- **Very short one-off scripts** — the overhead of persistent memory isn't worth it.
- **Work you want to forget** — if you explicitly don't want memory carryover, use Claude Code or Codex instead.
- **No network connectivity** — Letta Code needs the Letta API to persist memory. Purely offline work may prefer a local-only tool.

For everything else where you want a collaborator that gets smarter about your project over time, Letta Code is the move.

---

## Related Resources

- [letta-code GitHub](https://github.com/letta-ai/letta-code)
- [Letta Code release notes](https://github.com/letta-ai/letta-code/releases)
- [Letta Code docs](https://docs.letta.com/letta-code/)
- [Blog: Letta Code launch](https://www.letta.com/blog/letta-code)
- [Blog: Letta Code app](https://www.letta.com/blog/introducing-the-letta-code-app)
- [Learning SDK](https://github.com/letta-ai/learning-sdk) — for adding Letta-style memory to non-Letta agents
- [AI-Memory SDK](https://github.com/letta-ai/ai-memory-sdk) — experimental pluggable memory

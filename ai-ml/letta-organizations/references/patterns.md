# Letta Multi-Agent Patterns & Architecture

Advanced patterns for building and managing agent organizations. Use this reference
when Clay asks how to architect new agent interactions, coordinate agents, or implement
organizational-scale patterns.

## Table of Contents
1. [Memory Architecture](#memory-architecture)
2. [Shared Memory Blocks](#shared-memory-blocks)
3. [Multi-Agent Communication Patterns](#multi-agent-communication-patterns)
4. [Organizational Topologies](#organizational-topologies)
5. [Sleep-Time Agents](#sleep-time-agents)
6. [Task Board Pattern](#task-board-pattern)
7. [Compliance Enforcement Architecture](#compliance-enforcement-architecture)
8. [Community Patterns](#community-patterns)
9. [Model Swap Patterns](#model-swap-patterns)
10. [AsyncLetta Patterns](#asyncletta-patterns)
11. [Vercel AI SDK Integration](#vercel-ai-sdk-integration)
12. [Learning SDK & AI-Memory SDK](#learning-sdk--ai-memory-sdk)

---

## Memory Architecture

Letta uses a three-tier memory model that maps to cognitive science concepts:

### Tier 1 — Core (In-Context) Memory
Always in the LLM's context window. Consists of labeled blocks.

**Default blocks:**
```
[persona]   → Who the agent is, its personality and purpose
[human]     → Who it's talking to, their context and preferences
```

**Custom blocks (any label):**
```
[current_tasks]     → Active work items
[project_context]   → Current project state
[org_standards]     → Organizational compliance rules
[known_agents]      → Map of other agents in the org
```

Memory blocks render as XML-tagged sections in the prompt:
```xml
<memory>
  <core>
    <persona character_limit="20000" characters_used="342">
      You are ResearchBot, specializing in...
    </persona>
    <human character_limit="20000" characters_used="189">
      The user is Clay, working on the Paperclip platform...
    </human>
  </core>
</memory>
```

Block limits: 20,000 chars by default. Configurable per block. Agents self-edit via
`core_memory_append` and `core_memory_replace` tools.

### Tier 2 — Archival (Long-Term) Memory
External storage accessed via semantic search. Not always in context.

Use for: research results, historical task logs, learned patterns, large knowledge bases.

Agents insert: `archival_memory_insert("key fact to remember")`
Agents retrieve: `archival_memory_search("query about what I need")` → top-k results

### Tier 3 — Recall (Conversation History)
Stored message database. Searchable but not always in context.

Agents query: `conversation_search("something the user mentioned earlier")`

---

## Shared Memory Blocks

Multiple agents can mount the same memory block, enabling real-time state sharing
without message passing.

### Creating a Shared Block
```python
import requests, os

# 1. Create the shared block
r = requests.post(
    "https://api.letta.com/v1/blocks",
    headers={"Authorization": f"Bearer {os.environ['LETTA_API_KEY']}"},
    json={
        "label": "org_task_board",
        "value": "# Org Task Board\n\nNo tasks yet.",
        "limit": 20000,
        "description": "Shared task board for all Donjon agents"
    }
)
shared_block_id = r.json()["id"]

# 2. Mount on multiple agents
for agent_id in agent_ids:
    requests.post(
        f"https://api.letta.com/v1/agents/{agent_id}/memory/blocks/attach",
        headers={"Authorization": f"Bearer {os.environ['LETTA_API_KEY']}"},
        json={"id": shared_block_id}
    )
```

When any agent writes to this block via `core_memory_replace`, all other agents
see the update the next time they use it. This is the foundation of org-wide
state propagation without explicit message routing.

### Useful Shared Block Patterns

**Org task board** — all agents can read and update tasks:
```
# Donjon Task Board
## Agent: ResearchBot | Status: active
- [IN PROGRESS] Research Letta API patterns
- [DONE] Summarize SDK docs

## Agent: WriterBot | Status: idle
- [PENDING] Draft blog post on agent architecture
```

**Known agents registry** — agents can discover each other:
```
## Agent Registry
- research-agent-001 | role: research | tags: research,v2
- writer-agent-001 | role: content | tags: writing,v1
- coordinator-001 | role: orchestrator | tags: coord,primary
```

**Org standards block** — compliance rules read by all agents:
```
# Donjon Intelligence Systems — Agent Standards
Version: 2.1 | Updated: 2026-04-07

## Communication Style
- Always use professional tone in external comms
- Internal agent-to-agent messages may be terse

## Tool Usage
- Confirm destructive actions before executing
- Log all external API calls to archival memory

## Task Protocol
- Update [current_tasks] block before starting any task
- Mark tasks done within 60 seconds of completion
```

---

## Multi-Agent Communication Patterns

### Synchronous Call (request/response)
One agent calls another and waits for the reply. Good for: routing, delegation, fact-checking.

```python
# Agent A calls Agent B synchronously
# Agent A's perspective: uses send_message_to_agent_and_wait_for_reply tool
# Result: blocking — A pauses until B responds

# In Clay's API context — trigger from outside:
# Send a message to the orchestrator and let it route to subagents
response = client.agents.messages.send(
    agent_id=orchestrator_id,
    messages=[{"role": "user", "content": "Research letta memory architecture"}]
)
```

### Asynchronous Fire-and-Forget
Agent fires a message to another agent without waiting. Good for: background tasks,
notifications, parallel work distribution.

```python
# Agent A dispatches to Agent B without blocking
# Agent B will process and optionally report back later
# Use when: parallel workloads, non-blocking handoffs
```

### Broadcast to Tagged Group
Send the same message to all agents matching a tag. Good for: org-wide announcements,
distributing the same task to multiple specialized agents.

```python
# "Send this compliance update to all agents tagged 'v2'"
# Uses: send_message_to_agents_matching_tags
# Tags must be set on agents at creation or via PATCH /v1/agents/{id}
```

### Tag-Based Routing
Set tags on agents to create logical groups: `["research"]`, `["writing"]`, `["qa"]`.
The orchestrator can then route tasks to the right group without knowing exact agent IDs.

```python
# Update agent tags
requests.patch(
    f"https://api.letta.com/v1/agents/{agent_id}",
    headers={"Authorization": f"Bearer {os.environ['LETTA_API_KEY']}"},
    json={"tags": ["research", "v2", "active"]}
)
```

---

## Organizational Topologies

### Hub-and-Spoke (most common)
One orchestrator agent routes to N specialist agents.
```
Orchestrator
├── ResearchBot (sync)
├── WriterBot (sync)
└── QABot (async)
```
Best for: task delegation, specialized workloads, when Clay interacts with one endpoint.

### Peer Mesh
Agents communicate directly with each other without a central hub.
```
AgentA ←→ AgentB
  ↕           ↕
AgentC ←→ AgentD
```
Best for: distributed research, when no clear hierarchy exists.
Risk: harder to audit, circular dependencies possible.

### Cognitive/Biological Model (from Lethe project)
Maps agent roles to cognitive functions:
- **Cortex** (main agent) — user-facing, quick tasks, delegation
- **Default Mode Network** — background, scans goals, generates reflections
- **Salience Monitor** (Amygdala) — detects urgency, escalates
- **Subagents** — spawned per task, report only to parent

Best for: executive assistant patterns, always-on agent systems.

### Pipeline
Linear chain where each agent transforms output for the next.
```
InputAgent → ProcessorAgent → OutputAgent → DeliveryAgent
```
Best for: document processing, structured transformation workflows.

### Generating a Topology Flowchart
```python
import json, requests, os

def build_topology(api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    agents = requests.get("https://api.letta.com/v1/agents", headers=headers).json()
    
    lines = ["graph TD"]
    for agent in agents:
        label = f'{agent["id"][:8]}["{agent["name"]}\\n({", ".join(agent.get("tags", [])[:2])})"]'
        lines.append(f"    {label}")
        
        # Check which multi-agent tools are attached
        tools_r = requests.get(f'https://api.letta.com/v1/agents/{agent["id"]}/tools', headers=headers)
        tools = [t["name"] for t in tools_r.json()]
        if "send_message_to_agent_and_wait_for_reply" in tools:
            lines.append(f"    %% {agent['name']} can call agents synchronously")
        if "send_message_to_agents_matching_tags" in tools:
            lines.append(f"    %% {agent['name']} can broadcast")
    
    return "\n".join(lines)
```

---

## Sleep-Time Agents

Background agents that run on schedules without user interaction.

### Use Cases
- **Memory consolidation** — review and compress archival memory
- **Goal scanning** — check if current tasks align with long-term objectives
- **System prompt improvement** — analyze conversations and refine persona blocks
- **Compliance sweeps** — periodically verify all agents meet org standards
- **Report generation** — daily/weekly digests of agent activity

### Pattern: Sleep-Time Compliance Monitor
```python
# 1. Create a "compliance monitor" agent with these tools:
# - send_message_to_agents_matching_tags (to check all agents)
# - core_memory_replace (to update its own compliance report block)
# - archival_memory_insert (to log findings)

# 2. Send it a scheduled task:
compliance_message = """
Review all agents tagged 'production'. For each:
1. Verify persona block is non-empty and role-appropriate
2. Verify they have send_message tool attached
3. Update your [compliance_report] block with findings
4. Escalate any agent with 2+ violations
"""
```

### Triggering Scheduled Execution
Letta itself doesn't have a native cron, but you can:
- Use Paperclip's built-in scheduling (it's a control plane, after all)
- Use an external cron that hits the Letta API
- Use the Cowork `schedule` skill to create a recurring task that calls the Letta API

---

## Task Board Pattern

Implement distributed task tracking using shared memory blocks.

### Setup
```python
TASK_BOARD_TEMPLATE = """
# Donjon Task Board
Last updated: {timestamp}

## Pending
{pending_tasks}

## In Progress
{in_progress_tasks}

## Done (last 24h)
{done_tasks}
"""

# Read current task board
def read_task_board(api_key, coordinator_id):
    r = requests.get(
        f"https://api.letta.com/v1/agents/{coordinator_id}/memory/blocks/task_board",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    return r.json()["value"]

# Add a task
def add_task(api_key, coordinator_id, task_text, assigned_agent="unassigned"):
    board = read_task_board(api_key, coordinator_id)
    new_task = f"- [ ] {task_text} [{assigned_agent}]"
    # Append to pending section
    updated = board.replace("## Pending\n", f"## Pending\n{new_task}\n")
    requests.put(
        f"https://api.letta.com/v1/agents/{coordinator_id}/memory/blocks/task_board",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"value": updated}
    )
```

---

## Compliance Enforcement Architecture

### Org Standards Definition
Maintain a canonical `standards.json` that defines what a compliant agent looks like:

```json
{
  "version": "2.1",
  "required_blocks": ["persona", "human"],
  "required_tools": ["send_message"],
  "model_whitelist": ["claude-opus-4-5", "claude-sonnet-4-6"],
  "required_tags": ["donjon"],
  "persona_required_phrases": ["Donjon Intelligence Systems"],
  "max_stale_days": 30
}
```

### Compliance Check Script
```python
def check_compliance(agent, standards, api_key):
    results = {}
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Check memory blocks
    blocks_r = requests.get(f'https://api.letta.com/v1/agents/{agent["id"]}/memory/blocks', headers=headers)
    block_labels = {b["label"] for b in blocks_r.json()}
    block_values = {b["label"]: b["value"] for b in blocks_r.json()}
    
    for req_block in standards["required_blocks"]:
        results[f"has_{req_block}_block"] = req_block in block_labels and bool(block_values.get(req_block, "").strip())
    
    # Check tools
    tools_r = requests.get(f'https://api.letta.com/v1/agents/{agent["id"]}/tools', headers=headers)
    tool_names = {t["name"] for t in tools_r.json()}
    for req_tool in standards["required_tools"]:
        results[f"has_{req_tool}"] = req_tool in tool_names
    
    # Check model
    results["model_compliant"] = agent.get("model") in standards["model_whitelist"]
    
    # Check tags
    agent_tags = set(agent.get("tags", []))
    results["has_required_tags"] = bool(agent_tags & set(standards["required_tags"]))
    
    # Check persona content
    persona = block_values.get("persona", "")
    for phrase in standards.get("persona_required_phrases", []):
        results[f"persona_contains_{phrase[:20]}"] = phrase.lower() in persona.lower()
    
    return results

def compliance_report(api_key, standards):
    agents = list_all_agents(api_key)
    rows = []
    for agent in agents:
        checks = check_compliance(agent, standards, api_key)
        rows.append({"agent": agent["name"], "id": agent["id"], **checks})
    return rows
```

---

## Community Patterns

### Neuroscience-Inspired Cognitive Roles (from Lethe project)
Instead of "researcher/writer" specialization, assign roles based on cognitive function:

| Agent | Function | Always Running? |
|-------|----------|----------------|
| Cortex | User-facing, quick tasks, delegation | Yes |
| Default Mode Network | Goal scanning, reflection, memory consolidation | Background |
| Salience Monitor | Urgency detection, escalation | Background |
| Subagents | Task workers, report to parent only | Spawned on demand |

### Dynamic Tool Loading (from Project Thoth)
Prevent context bloat by loading tools only when a skill is active:
- Start each agent with only 4 core tools
- When activating a "skill", attach its tools via API
- When skill is done, detach tools
- Track loaded skills in a `loaded_skills` memory block

### Memory Interception for Retrofitting
Use the Letta Learning SDK pattern to add memory to any existing LLM call:
```python
# Wrap any openai/anthropic call with memory
with learning(agent="existing-agent"):
    response = client.chat.completions.create(...)
    # Automatically stores + retrieves relevant context
```

### Channel-Agnostic Context Injection
When routing messages from different sources to the same agent, prefix with context:
```python
def format_message(source: str, username: str, content: str) -> str:
    prefixes = {
        "dm": f"[{username} sent you a direct message]",
        "mention": f"[{username} mentioned you in #{source}]",
        "reply": f"[{username} replied to you in #{source}]"
    }
    prefix = prefixes.get(source, f"[{username} sent a message in #{source}]")
    return f"{prefix}\n\n{content}"
```
This allows one agent to handle multiple communication contexts with appropriate social awareness.

### GNAP: Git-Native Agent Protocols
Use git as a coordination substrate, Letta as cognitive substrate:
- `board/todo/` — unclaimed tasks (files with task specs)
- `board/doing/` — claimed by a specific agent
- `board/done/` — completed with output

Agents claim tasks by moving files. Letta memory stores their cognitive state about the task.
Works well for async workflows where agents don't need to communicate directly.

---

## Model Swap Patterns

Letta agents are model-portable — change the backing model without losing memory, persona, identity, or context. This is one of Letta's biggest structural advantages.

### Pattern: Planner / Executor Split

Use an expensive model for planning, a cheap one for execution, all within one persistent agent:

```python
from letta_client import Letta
import os

client = Letta(token=os.environ["LETTA_API_KEY"])

# Planning phase — expensive, high-quality reasoning
client.agents.modify(agent_id=agent_id, model="letta/kimi-k2.5")  # or gpt-4o, opus
plan_response = client.agents.messages.create(
    agent_id=agent_id,
    messages=[{"role": "user", "content": "Decompose this task into steps"}],
)

# Extract steps from plan, then execute cheaply
client.agents.modify(agent_id=agent_id, model="openai/gpt-4o-mini")  # cheap execution
for step in extracted_steps:
    client.agents.messages.create(
        agent_id=agent_id,
        messages=[{"role": "user", "content": step}],
    )

# Reflection — medium-quality summarization
client.agents.modify(agent_id=agent_id, model="google/gemini-2.0-flash")
reflection = client.agents.messages.create(
    agent_id=agent_id,
    messages=[{"role": "user", "content": "Summarize what was accomplished"}],
)
```

Cost savings compound: Opus-class thinking on ~5% of calls, cheap models on 95%. Memory ties it together.

### Pattern: Provider Failover

When a provider has a hiccup (rate limit, outage, deprecation):

```python
def send_with_failover(agent_id: str, message: str, model_chain: list[str]):
    for model in model_chain:
        try:
            client.agents.modify(agent_id=agent_id, model=model)
            return client.agents.messages.create(
                agent_id=agent_id,
                messages=[{"role": "user", "content": message}],
            )
        except Exception as e:
            print(f"Model {model} failed: {e}, trying next")
    raise RuntimeError("All models in chain failed")

send_with_failover(
    agent_id=agent_id,
    message="Do the thing",
    model_chain=["letta/kimi-k2.5", "openai/gpt-4o-mini", "google/gemini-2.0-flash"],
)
```

### Pattern: A/B Test Models Without Duplicating Agents

Test a new model on production traffic without creating a parallel agent:

```python
import random

MODELS = {
    "control": "letta/kimi-k2.5",
    "variant": "openai/gpt-4o-mini",
}

def chat(agent_id: str, message: str):
    arm = "variant" if random.random() < 0.1 else "control"  # 10% traffic to variant
    client.agents.modify(agent_id=agent_id, model=MODELS[arm])
    response = client.agents.messages.create(agent_id=agent_id, messages=[{"role": "user", "content": message}])
    log_metrics(arm=arm, response=response)
    return response
```

**Caveat:** model-swap mid-session is fast but not free. Batch model swaps at conversation boundaries, not per-message, unless you explicitly need per-message model routing.

### Pattern: Constraint-Driven Model Selection

Different models excel at different tasks. Route by task type:

```python
MODEL_BY_TASK = {
    "coding":        "anthropic/claude-sonnet-4-6",  # self-hosted only on Letta-served; Letta Code on Cloud
    "reasoning":     "letta/kimi-k2.5",
    "quick_replies": "openai/gpt-4o-mini",
    "long_context":  "google/gemini-2.0-flash",      # big context window
}

def route(agent_id: str, task_type: str, message: str):
    client.agents.modify(agent_id=agent_id, model=MODEL_BY_TASK[task_type])
    return client.agents.messages.create(agent_id=agent_id, messages=[{"role": "user", "content": message}])
```

---

## AsyncLetta Patterns

The Python SDK has an async client (`AsyncLetta`) for concurrent operations. Use it when you're calling many agents or running long operations in parallel.

### Setup

```python
import asyncio
from letta_client import AsyncLetta
import os

aclient = AsyncLetta(token=os.environ["LETTA_API_KEY"])
```

### Pattern: Parallel Block Reads Across Agents

```python
async def snapshot_all_personas():
    agents = await aclient.agents.list(limit=200)

    async def get_persona(agent):
        blocks = await aclient.agents.blocks.list(agent_id=agent.id)
        persona = next((b for b in blocks if b.label == "persona"), None)
        return {"agent": agent.name, "persona": persona.value if persona else None}

    return await asyncio.gather(*[get_persona(a) for a in agents])

personas = asyncio.run(snapshot_all_personas())
```

Sync version: N sequential calls. Async: N parallel. For 100 agents, this is 100x faster wall-clock.

### Pattern: Parallel Fleet Chat

Send the same prompt to multiple specialists and merge results:

```python
async def fanout_and_merge(agent_ids: list[str], prompt: str):
    async def ask(agent_id):
        response = await aclient.agents.messages.create(
            agent_id=agent_id,
            messages=[{"role": "user", "content": prompt}],
        )
        return {"agent_id": agent_id, "response": response}

    results = await asyncio.gather(*[ask(a) for a in agent_ids])
    return results
```

Compare with the native **Supervisor group** — if this pattern is recurring, promote it to a `manager_type: "supervisor"` Group for host-managed routing. See `references/groups.md`.

### Pattern: Background Sweep With Bounded Concurrency

When updating many agents, use a semaphore to avoid rate limits:

```python
async def bulk_update_with_limit(agent_updater, agent_ids, concurrency=10):
    sem = asyncio.Semaphore(concurrency)

    async def guarded(agent_id):
        async with sem:
            return await agent_updater(agent_id)

    return await asyncio.gather(*[guarded(a) for a in agent_ids])

async def update_persona(agent_id):
    persona = await aclient.agents.blocks.retrieve(agent_id, "persona")
    new_value = persona.value + "\n\n[DONJON_STANDARDS_V3]"
    await aclient.agents.blocks.modify(agent_id, "persona", value=new_value)

asyncio.run(bulk_update_with_limit(update_persona, all_agent_ids, concurrency=10))
```

### Pattern: Streaming + Async

Async streaming for a real-time UI:

```python
async def stream_chat(agent_id: str, message: str):
    async for event in aclient.agents.messages.create_stream(
        agent_id=agent_id,
        messages=[{"role": "user", "content": message}],
        stream_tokens=True,
    ):
        yield event  # forward to SSE response, websocket, or similar
```

---

## Vercel AI SDK Integration

The [`@letta-ai/vercel-ai-sdk-provider`](https://github.com/letta-ai/vercel-ai-sdk-provider) makes a Letta agent a first-class Vercel AI SDK provider. Drops into any `useChat`-based app.

### Install

```sh
npm install @letta-ai/vercel-ai-sdk-provider ai
```

### Next.js App Router

```ts
// app/api/chat/route.ts
import { streamText } from "ai";
import { letta } from "@letta-ai/vercel-ai-sdk-provider";

export async function POST(req: Request) {
  const { messages, agentId } = await req.json();
  const result = await streamText({
    model: letta(agentId, { apiKey: process.env.LETTA_API_KEY! }),
    messages,
  });
  return result.toDataStreamResponse();
}
```

```tsx
// app/chat/page.tsx
"use client";
import { useChat } from "ai/react";

export default function ChatPage() {
  const { messages, input, handleInputChange, handleSubmit } = useChat({
    api: "/api/chat",
    body: { agentId: "agent-abc123" },
  });
  return (
    <>
      {messages.map((m) => <div key={m.id}><b>{m.role}:</b> {m.content}</div>)}
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} />
      </form>
    </>
  );
}
```

### Pattern: Per-User Agents Via Identities + Vercel

Combine Identities (per-user scoping) with the Vercel provider (Next.js chat UI):

```ts
// app/api/chat/route.ts
import { streamText } from "ai";
import { letta } from "@letta-ai/vercel-ai-sdk-provider";
import { LettaClient } from "@letta-ai/letta-client";
import { auth } from "@/lib/auth"; // your auth of choice

const client = new LettaClient({ token: process.env.LETTA_API_KEY! });
const SHARED_AGENT_ID = "agent-support-shared";

export async function POST(req: Request) {
  const session = await auth();
  const { messages } = await req.json();

  // Upsert identity for this user
  const identity = await client.identities.upsert({
    identifierKey: session.user.email,
    name: session.user.name,
    identityType: "user",
  });

  const result = await streamText({
    model: letta(SHARED_AGENT_ID, {
      apiKey: process.env.LETTA_API_KEY!,
      identityId: identity.id,  // scopes the agent to this user's blocks
    }),
    messages,
  });
  return result.toDataStreamResponse();
}
```

One shared agent, per-user scoped memory, Next.js chat UI. Multi-tenancy without duplicating agents.

### Why use the Vercel provider over raw SDK calls?

- You already use Vercel AI SDK hooks (`useChat`, `useCompletion`)
- You want automatic streaming UI state management
- You want framework-agnostic SSE handling (Next.js, Remix, SvelteKit)
- You want provider-swappable code (drop-in OpenAI → Letta migration path)

For server-only code or non-React apps, use `@letta-ai/letta-client` directly.

---

## Learning SDK & AI-Memory SDK

Two experimental SDKs from Letta for adding Letta-style memory to non-Letta agents.

### Learning SDK

Upstream: [github.com/letta-ai/learning-sdk](https://github.com/letta-ai/learning-sdk)

Purpose: drop-in SDK for adding continual learning and long-term memory to *any* LLM agent (not just Letta-backed ones). You wrap your OpenAI/Anthropic/Google call with a learning context manager, and it transparently stores and retrieves relevant context using Letta's memory layer underneath.

```python
# Pseudocode — confirm exact API in the SDK README
from letta_learning import learning

with learning(agent="my-external-agent"):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[...],
    )
    # Learning SDK automatically stores facts from the exchange
    # Next call within the same context retrieves relevant prior facts
```

Use when:
- You have an existing agent infrastructure (LangChain, LlamaIndex, custom) and want Letta-style memory without migrating to Letta agents
- You want to A/B test whether memory improves outcomes before committing to Letta
- You need memory on a codebase you can't fully rewrite to use Letta primitives

### AI-Memory SDK

Upstream: [github.com/letta-ai/ai-memory-sdk](https://github.com/letta-ai/ai-memory-sdk)

Purpose: experimental, lower-level, pluggable memory substrate. Decouples the memory storage/retrieval layer from the agent runtime entirely. Useful as a library for building custom memory-aware tools or experiments.

Still marked experimental — API is unstable. Use Letta agents directly for production; reach for ai-memory-sdk only for research or custom memory subsystems.

### When To Use Each

| Tool | Use Case | Stability |
|---|---|---|
| `letta-client` (Python/TS) | Full Letta agent — you want the whole stateful agent model | Stable |
| `letta-node` Vercel provider | Web UI with Letta agents behind useChat | Stable |
| `learning-sdk` | Bolt-on memory for non-Letta agents | Newer; check README for version |
| `ai-memory-sdk` | Research / custom memory layer | Experimental |
| `letta-code` | Coding CLI with persistent memory | Stable |

For Clay's "serious work" posture: Letta agents + `letta-client` + optional `letta-code` for coding sessions is the 90% path. Learning SDK if retrofitting an existing non-Letta system. Skip ai-memory-sdk unless building custom memory plumbing.

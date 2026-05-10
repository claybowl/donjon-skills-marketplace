# Groups — Native Multi-Agent Coordination

**Groups** are Letta's first-class multi-agent primitive. Instead of hand-wiring `send_message_to_agent_*` tools between agents (the legacy pattern in `patterns.md`), you declare a group, attach agents to it, pick a manager type, and the group becomes the addressable unit for coordination.

Upstream: [docs.letta.com/guides/agents/groups/](https://docs.letta.com/guides/agents/groups/)

---

## When To Reach For A Group

Use a Group when:

- You have a coordination pattern that fits one of the built-in manager types (supervisor, round-robin, dynamic, sleeptime)
- You want messages routed **to the group** rather than to a specific agent
- You want the manager's coordination logic to be **host-provided**, not reimplemented per plugin
- You want to swap coordination patterns without rewiring tools on every agent

Stick with tool-wired `send_message_to_agent_*` when:

- Your coordination doesn't match any group manager type
- You're doing ad-hoc peer-to-peer communication
- Group semantics (e.g. fixed member list, manager routing) don't fit your use case

---

## The Group Object

```ts
interface Group {
  id: string;                 // "group-abc123"
  name?: string;
  manager_type: "round_robin" | "supervisor" | "dynamic" | "sleeptime";
  agent_ids: string[];        // members
  manager_agent_id?: string;  // required for supervisor, dynamic
  max_turns?: number;         // for round_robin and dynamic
  termination_token?: string; // for dynamic — string the manager outputs to stop
  sleeptime_agent_frequency?: number; // for sleeptime — every N steps
  description?: string;
  hidden?: boolean;
  project_id?: string;
  created_at: string;
  updated_at: string;
}
```

---

## Manager Types

### `round_robin`

Rotates through agents in order. Each agent gets one turn per rotation. Good for:

- Brainstorming where you want each specialist to weigh in once
- Formal debate structures
- Peer review cycles

```python
group = client.groups.create(
    manager_type="round_robin",
    agent_ids=[researcher_id, writer_id, critic_id],
    max_turns=6,  # stops after 6 total turns (2 rotations)
)
```

### `supervisor`

One manager agent routes prompts to worker agents and aggregates their responses. Good for:

- Delegation ("break this task down and dispatch")
- Parallel specialist consultation with synthesis
- Orchestrator patterns

```python
# Create the supervisor agent first
supervisor = client.agents.create(
    name="research_supervisor",
    model="letta/kimi-k2.5",
    memory_blocks=[{"label": "persona", "value": "You supervise specialist agents and synthesize their outputs into a final answer."}],
)

group = client.groups.create(
    manager_type="supervisor",
    manager_agent_id=supervisor.id,
    agent_ids=[researcher_id, writer_id, fact_checker_id],
)

# Send to the group → supervisor routes
response = client.groups.messages.create(
    group_id=group.id,
    messages=[{"role": "user", "content": "Write a 500-word brief on stateful agents"}],
)
```

The supervisor forwards the prompt to all workers, receives their responses, and produces a final synthesis.

### `dynamic`

The manager chooses which agent to speak next based on context. Group runs until the manager emits a `termination_token` or `max_turns` is reached. Good for:

- Adaptive conversations where the manager reads room and picks the best next speaker
- Workflows where the right agent depends on what was just said
- Debate formats with a judge

```python
judge = client.agents.create(
    name="debate_judge",
    model="letta/kimi-k2.5",
    memory_blocks=[{"label": "persona", "value": "You moderate a debate. Pick the next speaker. When the debate is resolved, say 'DEBATE_CLOSED' to stop."}],
)

group = client.groups.create(
    manager_type="dynamic",
    manager_agent_id=judge.id,
    agent_ids=[advocate_a_id, advocate_b_id, neutral_id],
    termination_token="DEBATE_CLOSED",
    max_turns=20,
)
```

### `sleeptime`

One primary user-facing agent plus N background "sleep-time" agents. Background agents run every `sleeptime_agent_frequency` steps to maintain shared memory blocks. Good for:

- Always-on assistants with background memory consolidation
- Cognitive-architecture patterns (e.g. Default Mode Network, Salience Monitor from the Lethe community pattern)
- Long-running agents that need periodic reflection

```python
primary = client.agents.create(
    name="assistant",
    model="letta/kimi-k2.5",
    memory_blocks=[...],
    enable_sleeptime=True,           # shortcut — auto-wires tools
    sleeptime_agent_frequency=5,     # every 5 steps
)
# Letta auto-creates a sleep-time agent sharing the primary's memory blocks

# For more control, create them manually and wire the group:
reflection_agent = client.agents.create(
    name="reflection",
    model="letta/kimi-k2.5",
    memory_blocks=[...],  # shared_block_ids should match primary's
)

group = client.groups.create(
    manager_type="sleeptime",
    manager_agent_id=primary.id,
    agent_ids=[reflection_agent.id],  # multiple sleep-time agents allowed
    sleeptime_agent_frequency=5,
)
```

See also `patterns.md` §Sleep-Time Agents for the community usage patterns.

---

## API Reference

### List Groups

```
GET /v1/groups
```

Params: `limit`, `before`, `after`, `project_id`.

### Get Group

```
GET /v1/groups/{group_id}
```

### Create Group

```
POST /v1/groups
```

Body shape depends on `manager_type` (see above examples).

### Update Group

```
PATCH /v1/groups/{group_id}
```

Common fields: `agent_ids` (swap members), `manager_agent_id`, `max_turns`, `description`.

### Delete Group

```
DELETE /v1/groups/{group_id}
```

Does **not** delete member agents — just the group binding.

### Send Message to Group

```
POST /v1/groups/{group_id}/messages
```

Same request body as agent messages (`messages`, `stream_steps`, `stream_tokens`, `max_steps`). Manager routes internally.

### Stream Message to Group

```
POST /v1/groups/{group_id}/messages/stream
```

SSE stream. Events include per-agent messages, manager routing decisions, and the final synthesis.

### List Group Messages

```
GET /v1/groups/{group_id}/messages
```

Aggregated message log across all member agents during group runs.

### Attach / Detach Agents

```
POST /v1/groups/{group_id}/agents/attach
Body: { "agent_id": "agent-xyz" }

POST /v1/groups/{group_id}/agents/detach
Body: { "agent_id": "agent-xyz" }
```

---

## SDK Examples

### Python

```python
from letta_client import Letta
import os

client = Letta(token=os.environ["LETTA_API_KEY"])

# Create supervisor group
group = client.groups.create(
    manager_type="supervisor",
    manager_agent_id=supervisor_id,
    agent_ids=[worker_a_id, worker_b_id],
    description="Research supervisor with two workers",
)

# Send to the group
response = client.groups.messages.create(
    group_id=group.id,
    messages=[{"role": "user", "content": "Research X and write a summary"}],
)

# Stream
for event in client.groups.messages.create_stream(
    group_id=group.id,
    messages=[{"role": "user", "content": "Start the debate on Y"}],
):
    print(event.message_type, event)
```

### TypeScript

```ts
import { LettaClient } from "@letta-ai/letta-client";

const client = new LettaClient({ token: process.env.LETTA_API_KEY! });

const group = await client.groups.create({
  managerType: "supervisor",
  managerAgentId: supervisorId,
  agentIds: [workerAId, workerBId],
});

const response = await client.groups.messages.create(group.id, {
  messages: [{ role: "user", content: "Research X and write a summary" }],
});
```

---

## Pattern: Hub-and-Spoke via Supervisor Group

The classic orchestrator pattern becomes one manager agent + a supervisor group:

```python
orchestrator = client.agents.create(
    name="orchestrator",
    model="letta/kimi-k2.5",
    memory_blocks=[{"label": "persona", "value": "You coordinate specialists."}],
)

group = client.groups.create(
    manager_type="supervisor",
    manager_agent_id=orchestrator.id,
    agent_ids=[researcher_id, writer_id, qa_id],
)

# External interface: send everything to the group
def ask(prompt: str):
    return client.groups.messages.create(
        group_id=group.id,
        messages=[{"role": "user", "content": prompt}],
    )
```

The orchestrator's persona defines routing logic in natural language. You don't need to wire tools; the group manager does the routing.

---

## Pattern: Cognitive Architecture via Sleeptime

Map Lethe-style cognitive roles onto a sleep-time group:

```python
cortex = client.agents.create(
    name="cortex",
    model="letta/kimi-k2.5",
    memory_blocks=[
        {"label": "persona", "value": "You are the user-facing executive agent."},
        {"label": "shared_memory", "value": "", "limit": 40000},  # shared with DMN
    ],
)

default_mode_network = client.agents.create(
    name="default_mode_network",
    model="letta/kimi-k2.5",
    memory_blocks=[
        {"label": "persona", "value": "You reflect on recent cortex activity and consolidate shared memory."},
        {"label": "shared_memory", "value": "", "limit": 40000, "id": cortex_shared_block_id},
    ],
)

group = client.groups.create(
    manager_type="sleeptime",
    manager_agent_id=cortex.id,
    agent_ids=[default_mode_network.id],
    sleeptime_agent_frequency=5,
)
```

Every 5 cortex steps, the DMN runs in the background, reading cortex's recent activity and updating the shared memory block. Next cortex step sees the consolidated summary.

---

## Pattern: Debate Format via Dynamic

```python
judge = client.agents.create(
    name="judge",
    model="letta/kimi-k2.5",
    memory_blocks=[{"label": "persona", "value": """
You moderate a debate between Pro and Con. Pick the next speaker based on who should rebut or advance.
When one side has clearly won or the debate is stuck, emit exactly: DEBATE_CLOSED
"""}],
)

pro = client.agents.create(name="pro", memory_blocks=[{"label": "persona", "value": "Argue in favor."}], model="letta/kimi-k2.5")
con = client.agents.create(name="con", memory_blocks=[{"label": "persona", "value": "Argue against."}], model="letta/kimi-k2.5")

debate = client.groups.create(
    manager_type="dynamic",
    manager_agent_id=judge.id,
    agent_ids=[pro.id, con.id],
    termination_token="DEBATE_CLOSED",
    max_turns=20,
)
```

---

## Groups vs Hand-Wired Tools — Decision Tree

```
Need multi-agent coordination?
├── Does the pattern match supervisor / round_robin / dynamic / sleeptime?
│   ├── Yes → Use a Group. Less wiring, host-managed, clean semantics.
│   └── No → Use send_message_to_agent_* tools with your own coordination logic.
├── Is the member list stable?
│   ├── Yes → Groups are a clean fit.
│   └── No (members dynamically come/go) → Tools or periodic group updates via PATCH.
└── Do you need external-to-agent broadcast (not between agents)?
    └── Use send_message_to_agents_matching_tags (tag-based, no group required).
```

---

## Gotchas

- **Groups don't replace Identities** — a group is about coordination, not multi-tenancy. Use Identities for user scoping.
- **Manager agents count as agents** — a supervisor group with 3 workers needs 4 agents total.
- **Deleting a group doesn't delete its agents** — the agents persist and can be reused in other groups.
- **Sleep-time frequency is per-step, not wall-clock** — if your primary agent is idle, the sleep-time agent doesn't run on a timer; it waits for steps.
- **`max_turns` protects you** — always set it on round_robin and dynamic groups. Without it, a chatty group can loop until budget/context runs out.

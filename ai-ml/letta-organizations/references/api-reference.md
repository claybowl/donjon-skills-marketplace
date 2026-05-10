# Letta REST API Reference

Full endpoint catalog for Letta Cloud (`https://api.letta.com/v1`) and self-hosted.

## Table of Contents
1. [Authentication](#authentication)
2. [Agents](#agents)
3. [Messages](#messages)
4. [Memory & Blocks](#memory--blocks)
5. [Tools](#tools)
6. [Tool Rules](#tool-rules)
7. [Archives & Sources](#archives--sources)
8. [Identities](#identities)
9. [Groups](#groups)
10. [Templates](#templates)
11. [Projects](#projects)
12. [Runs](#runs)
13. [Users & Organizations](#users--organizations)
14. [Models & Embeddings](#models--embeddings)
15. [Pagination](#pagination)
16. [Error Codes](#error-codes)

---

## Authentication

All requests require:
```
Authorization: Bearer <LETTA_API_KEY>
Content-Type: application/json
```

API keys are scoped to an organization. Never log them.

---

## Agents

### List Agents
```
GET /v1/agents
```
Params: `limit` (int), `before` (cursor), `after` (cursor), `tags` (string[]), `name` (string)

Response:
```json
[{
  "id": "agent-abc123",
  "name": "string",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "description": "string",
  "system": "system prompt text",
  "model": "claude-opus-4-5",
  "embedding_model": "string",
  "tags": ["string"],
  "tools": [{"id": "tool-xyz", "name": "string"}],
  "memory_blocks": [{"label": "string", "limit": 20000}]
}]
```

### Get Agent
```
GET /v1/agents/{agent_id}
```
Returns full AgentState including model config, memory summary, tool list, and tags.

### Create Agent
```
POST /v1/agents
```
Body:
```json
{
  "name": "string",
  "description": "string",
  "system": "system prompt",
  "model": "letta/kimi-k2.5",
  "embedding_model": "text-embedding-ada-002",
  "tags": ["string"],
  "memory_blocks": [
    {"label": "persona", "value": "You are...", "limit": 20000},
    {"label": "human", "value": "The user is...", "limit": 20000}
  ],
  "tools": ["tool-id-1", "tool-id-2"],
  "max_tokens": 4096,
  "context_window_limit": 200000,
  "identity_ids": ["identity-abc"],
  "project_id": "proj-xyz",
  "enable_sleeptime": true,
  "sleeptime_agent_frequency": 5,
  "tool_rules": [
    {"type": "init", "tool_name": "core_memory_append"},
    {"type": "continue_loop", "tool_name": "archival_memory_search"},
    {"type": "terminate_loop", "tool_name": "send_message"}
  ]
}
```

**Model routing note:** When using a Letta-served model, prefix with `letta/` (e.g. `letta/kimi-k2.5`). When using your own provider key via Letta, use the provider prefix (e.g. `openai/gpt-4o-mini`, `google/gemini-2.0-flash`, `anthropic/claude-sonnet-4-6` in self-hosted only — Letta Cloud doesn't host Anthropic).

**Sleep-time fields (see Groups and Patterns for deeper usage):**
- `enable_sleeptime: true` — auto-provisions a sleep-time agent with `conversation_search` + `archival_memory_search` tools
- `sleeptime_agent_frequency: 5` — trigger cadence in steps (default 5)

### Update Agent
```
PATCH /v1/agents/{agent_id}
```
Partial update — send only fields to change. Common fields: `name`, `description`, `system`, `model`, `tags`.

### Delete Agent
```
DELETE /v1/agents/{agent_id}
```

### Export Agent (as .af file)
```
GET /v1/agents/{agent_id}/export
```

### Import Agent
```
POST /v1/agents/import
Content-Type: multipart/form-data
```

---

## Messages

### Send Message (Sync)
```
POST /v1/agents/{agent_id}/messages
```
Body:
```json
{
  "messages": [{"role": "user", "content": "string"}],
  "stream_steps": false,
  "stream_tokens": false,
  "max_steps": 50
}
```

Response includes a list of `LettaMessage` objects with discriminated union on `message_type`:
- `user_message` — what was sent
- `assistant_message` — visible text response
- `tool_call_message` — tool invocation (name + args)
- `tool_return_message` — tool execution result
- `reasoning_message` — internal chain-of-thought
- `system_message` — system-injected content

### Send Message (Streaming SSE)
```
POST /v1/agents/{agent_id}/messages/stream
```

Request body adds streaming controls:
```json
{
  "messages": [{"role": "user", "content": "string"}],
  "stream_tokens": true,     // true = token-level stream (granular, chatty)
  "stream_steps": false,     // true = step-level stream (coarser, cleaner)
  "max_steps": 50
}
```

Returns `text/event-stream`. Event types mirror `message_type`:
- `reasoning_message` — internal chain-of-thought (usually hide from UI)
- `tool_call_message` — `{tool_call: {name, arguments}}`
- `tool_return_message` — `{tool_return, tool_call_id}`
- `assistant_message` — `{content}` (the visible text)
- `stop_reason` — `{stop_reason}` (`"end_turn" | "max_steps" | "error"`)

**Async (long-running) messages** — for runs that may outlast a single HTTP connection, use async mode:

```
POST /v1/agents/{agent_id}/messages/async
```

Returns a `run_id`. Poll `GET /v1/runs/{run_id}` for status. Fetch results with `GET /v1/runs/{run_id}/messages`. See §Runs.

### List Messages (Conversation History)
```
GET /v1/agents/{agent_id}/messages
```
Params: `limit`, `before`, `after`, `msg_object` (bool — return full objects vs strings)

### Delete Messages
```
DELETE /v1/agents/{agent_id}/messages
```
Body: `{"message_ids": ["msg-123"]}`

### Batch Message (Async, multiple agents)
```
POST /v1/batches
```
Sends the same message to multiple agents asynchronously.

---

## Memory & Blocks

### Get All Memory Blocks for Agent
```
GET /v1/agents/{agent_id}/memory/blocks
```
Returns array of blocks with `label`, `value`, `limit`, `description`, `read_only`, `id`.

### Get Specific Block
```
GET /v1/agents/{agent_id}/memory/blocks/{block_label}
```

### Update Block Value
```
PUT /v1/agents/{agent_id}/memory/blocks/{block_label}
```
Body: `{"value": "new content string"}`

Note: in Python SDK this is `client.agents.blocks.update(block_label, agent_id=agent_id, value=...)`

### Create Custom Block
```
POST /v1/agents/{agent_id}/memory/blocks
```
Body:
```json
{
  "label": "current_tasks",
  "value": "initial content",
  "limit": 20000,
  "description": "Human-readable purpose",
  "read_only": false
}
```

### Delete Block
```
DELETE /v1/agents/{agent_id}/memory/blocks/{block_label}
```

### Archival Memory — Insert
```
POST /v1/agents/{agent_id}/archival-memory
```
Body: `{"text": "content to store"}`

### Archival Memory — Search
```
POST /v1/agents/{agent_id}/archival-memory/search
```
Body: `{"query": "semantic search query", "limit": 10}`

### Archival Memory — List
```
GET /v1/agents/{agent_id}/archival-memory
```

---

## Tools

### List All Org Tools
```
GET /v1/tools
```
Params: `limit`, `before`, `after`, `name` (filter)

### Get Tool
```
GET /v1/tools/{tool_id}
```

### Create Custom Tool
```
POST /v1/tools
```
Body:
```json
{
  "name": "my_tool",
  "description": "What the tool does",
  "source_code": "def my_tool(param: str) -> str:\n    '''docstring used as description'''\n    return result",
  "tags": ["custom"]
}
```
Tool source constraints: no local imports, credentials via `os.environ`, max name 48 chars.

### Update Tool
```
PUT /v1/tools/{tool_id}
```

### Delete Tool
```
DELETE /v1/tools/{tool_id}
```

### List Agent Tools
```
GET /v1/agents/{agent_id}/tools
```

### Attach Tool to Agent
```
POST /v1/agents/{agent_id}/tools/attach
```
Body: `{"tool_id": "tool-xyz"}`  
SDK: `client.agents.tools.attach(tool_id, agent_id=agent_id)`

### Detach Tool from Agent
```
POST /v1/agents/{agent_id}/tools/detach
```
Body: `{"tool_id": "tool-xyz"}`  
SDK: `client.agents.tools.detach(tool_id, agent_id=agent_id)`

### Built-in Tools (always available)
| Tool | Purpose |
|------|---------|
| `send_message` | Send visible reply to user |
| `core_memory_append` | Append to a memory block |
| `core_memory_replace` | Replace content in a memory block |
| `archival_memory_insert` | Add to long-term archival store |
| `archival_memory_search` | Semantic search archival store |
| `conversation_search` | Search message history |
| `send_message_to_agent_and_wait_for_reply` | Sync multi-agent call |
| `send_message_to_agent_async` | Async multi-agent call |
| `send_message_to_agents_matching_tags` | Broadcast to tagged agents |

---

## Tool Rules

Tool rules constrain the agent's sequencing of tool calls. Set on agent creation or via `PATCH /v1/agents/{id}`.

### Rule Types

| Type | Meaning |
|---|---|
| `init` | Tool that must run first in a step |
| `continue_loop` | Tool that keeps the agent looping (doesn't terminate the step) |
| `terminate_loop` | Tool that ends the step when called |
| `exclusive` | Tool that, when present in a step, blocks others of the same class |
| `requires_tool` | Tool that must be called before tool X (dependency) |

### Example

```json
{
  "tool_rules": [
    { "type": "init", "tool_name": "archival_memory_search" },
    { "type": "continue_loop", "tool_name": "core_memory_append" },
    { "type": "terminate_loop", "tool_name": "send_message" }
  ]
}
```

This agent must search archival first, may loop through memory appends, and terminates when it sends a user message. Great for ensuring consistent reasoning patterns across an agent fleet.

### When To Use Tool Rules

- **Reliability** — enforce "always search before answering"
- **Safety** — prevent an agent from calling a destructive tool without a precondition
- **Workflow shape** — enforce a specific step structure for a specialist agent (e.g. "always commit to memory before replying")

Tool rules are evaluated per-step. They don't replace the model's judgment; they constrain the space of valid action sequences.

---

## Archives & Sources

### List Archives
```
GET /v1/archives
```

### Create Archive
```
POST /v1/archives
```
Body: `{"name": "string", "description": "string"}`

### Upload to Archive
```
POST /v1/archives/{archive_id}/files
Content-Type: multipart/form-data
```

### Attach Archive to Agent
```
POST /v1/agents/{agent_id}/archives/attach
```
Body: `{"archive_id": "archive-xyz"}`

### Search Archive
```
POST /v1/archives/{archive_id}/search
```
Body: `{"query": "semantic query", "limit": 10}`

### Data Sources (streaming ingestion)

For continually-updated knowledge bases (vs fixed-document Archives):

```
GET /v1/sources
POST /v1/sources
GET /v1/sources/{source_id}
PATCH /v1/sources/{source_id}
DELETE /v1/sources/{source_id}
POST /v1/agents/{agent_id}/sources/attach
POST /v1/agents/{agent_id}/sources/detach
```

Sources support incremental indexing — append new documents without rebuilding. Use for evolving knowledge bases (Slack exports synced nightly, Notion page mirrors, etc.).

---

## Identities

First-class objects for user/org/custom scoping. See `references/identities.md` for patterns.

### List Identities
```
GET /v1/identities
```
Params: `limit`, `before`, `after`, `name`, `identifier_key`, `identity_type`, `project_id`

### Get Identity
```
GET /v1/identities/{identity_id}
```

### Get By Key (lookup)
```
GET /v1/identities/by-key/{identifier_key}
```

### Create Identity
```
POST /v1/identities
```
Body:
```json
{
  "name": "Clay",
  "identifier_key": "claydonjon@proton.me",
  "identity_type": "user",
  "block_ids": [],
  "properties": {"role": "admin"},
  "project_id": "proj-xyz"
}
```

`identity_type`: `"user" | "org" | "other"`

### Upsert (create-if-not-exists)
```
POST /v1/identities/upsert
```
Same body; returns existing if `identifier_key` matches.

### Update Identity
```
PATCH /v1/identities/{identity_id}
```

### Delete Identity
```
DELETE /v1/identities/{identity_id}
```

### Attach/Detach Blocks
```
POST /v1/identities/{identity_id}/blocks/attach
Body: {"block_id": "block-xyz"}

POST /v1/identities/{identity_id}/blocks/detach
Body: {"block_id": "block-xyz"}
```

### Send Message With Identity Scope

When calling `POST /v1/agents/{id}/messages`, add `identity_id` to the body to scope the agent to that identity's blocks for this call.

---

## Groups

Native multi-agent coordination. See `references/groups.md` for manager-type patterns.

### List Groups
```
GET /v1/groups
```

### Get Group
```
GET /v1/groups/{group_id}
```

### Create Group
```
POST /v1/groups
```

Body varies by `manager_type`:

**Supervisor:**
```json
{
  "manager_type": "supervisor",
  "manager_agent_id": "agent-supervisor",
  "agent_ids": ["agent-a", "agent-b"],
  "description": "string"
}
```

**Round-robin:**
```json
{
  "manager_type": "round_robin",
  "agent_ids": ["agent-a", "agent-b", "agent-c"],
  "max_turns": 6
}
```

**Dynamic:**
```json
{
  "manager_type": "dynamic",
  "manager_agent_id": "agent-judge",
  "agent_ids": ["agent-a", "agent-b"],
  "termination_token": "DONE",
  "max_turns": 20
}
```

**Sleep-time:**
```json
{
  "manager_type": "sleeptime",
  "manager_agent_id": "agent-primary",
  "agent_ids": ["agent-reflection"],
  "sleeptime_agent_frequency": 5
}
```

### Update Group
```
PATCH /v1/groups/{group_id}
```

### Delete Group
```
DELETE /v1/groups/{group_id}
```
(Does not delete member agents.)

### Attach / Detach Agents
```
POST /v1/groups/{group_id}/agents/attach
Body: {"agent_id": "agent-xyz"}

POST /v1/groups/{group_id}/agents/detach
Body: {"agent_id": "agent-xyz"}
```

### Send Message To Group
```
POST /v1/groups/{group_id}/messages
```
Same body shape as agent messages. The group's manager handles routing.

### Stream Message To Group
```
POST /v1/groups/{group_id}/messages/stream
```
SSE stream. Events include per-agent messages, manager routing decisions, and final synthesis.

### List Group Messages
```
GET /v1/groups/{group_id}/messages
```

---

## Templates

Block templates — reusable persona/human presets.

### List Templates
```
GET /v1/blocks?is_template=true
```

### Create Template
```
POST /v1/blocks
Body: {"label": "persona_support", "value": "...", "limit": 20000, "is_template": true, "description": "Standard support-agent persona"}
```

### Apply Template To Agent

On agent creation, reference a template by ID in `memory_blocks`:

```json
{
  "memory_blocks": [
    {"template_id": "block-template-xyz"},
    {"label": "human", "value": "", "limit": 20000}
  ]
}
```

Or copy-on-create: read the template, then create a fresh block with its value for the new agent. Copy-on-create is common — it lets the agent diverge from the template over time.

---

## Projects

Multi-tenant isolation within a Letta Cloud org.

### List Projects
```
GET /v1/projects
```

### Get Project
```
GET /v1/projects/{project_id}
```

### Create Project
```
POST /v1/projects
Body: {"name": "donjon-prod", "description": "Production Donjon agents"}
```

### Scope Entities To A Project

When creating agents, blocks, identities, groups — add `project_id: "proj-xyz"` to scope them. `GET /v1/agents?project_id=proj-xyz` filters to project-scoped agents.

Use projects to:
- Separate staging/prod agent fleets
- Isolate per-customer deployments (B2B SaaS)
- Keep experimental agents out of the main org inventory

---

## Runs

Background/async execution tracking.

### Get Run Status
```
GET /v1/runs/{run_id}
```
Status values: `created`, `queued`, `running`, `completed`, `failed`, `cancelled`

### List Runs for Agent
```
GET /v1/agents/{agent_id}/runs
```

### Get Run Messages
```
GET /v1/runs/{run_id}/messages
```

### Cancel Run
```
DELETE /v1/runs/{run_id}
```

---

## Users & Organizations

### List Users (org-scoped)
```
GET /v1/users
```

### Get Current User
```
GET /v1/users/me
```

### List Projects / Namespaces
```
GET /v1/projects
```
(Letta Cloud uses projects for multi-tenant isolation within an org)

---

## Models & Embeddings

### List Available LLMs
```
GET /v1/models
```

### List Embedding Models
```
GET /v1/embedding-models
```

---

## Pagination

All list endpoints use **cursor-based pagination**:

```python
# First page
r = requests.get("/v1/agents", params={"limit": 50})
agents = r.json()

# Next page — use last agent's id as cursor
if len(agents) == 50:
    r = requests.get("/v1/agents", params={"limit": 50, "after": agents[-1]["id"]})
```

To fetch ALL agents:
```python
def list_all_agents(api_key, base_url="https://api.letta.com"):
    headers = {"Authorization": f"Bearer {api_key}"}
    all_agents, after = [], None
    while True:
        params = {"limit": 100}
        if after:
            params["after"] = after
        r = requests.get(f"{base_url}/v1/agents", headers=headers, params=params)
        batch = r.json()
        all_agents.extend(batch)
        if len(batch) < 100:
            break
        after = batch[-1]["id"]
    return all_agents
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 401 | Invalid or missing API key |
| 403 | Insufficient permissions (agent belongs to different org) |
| 404 | Agent/block/tool not found |
| 422 | Validation error (check request body) |
| 429 | Rate limit exceeded |
| 500 | Letta server error |

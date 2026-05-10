# Identities — User / Org / Other Scoping

**Identities** are Letta's first-class primitive for binding agents and memory blocks to a real-world entity: an end user, an organization, or a custom scope. Without Identities, you'd have to duplicate agents per user. With them, one agent can serve many users with per-user memory through block bindings.

Upstream: [docs.letta.com/api-reference/identities/list](https://docs.letta.com/api-reference/identities/list)

---

## The Identity Object

```ts
interface Identity {
  id: string;                 // "identity-abc123"
  name: string;               // human name: "Clay", "Donjon Intelligence Systems"
  identifier_key: string;     // stable external key (email, user ID from your app, etc.)
  identity_type: "user" | "org" | "other";
  block_ids: string[];        // blocks bound to this identity
  properties: Record<string, unknown>; // free-form metadata
  project_id?: string;        // optional project scoping
  created_at: string;
  updated_at: string;
}
```

`identifier_key` is the **external** key — the thing your app already uses to name this entity. Typically an email, a Supabase user ID, a Clerk ID, a tenant slug. Letta uses `identifier_key` to look up the identity without you carrying `id` around.

---

## Why Identities Matter

**Without Identities:**

- You duplicate the same agent per user (hundreds of agents, each with a copy of the persona)
- Or you maintain a single agent and stuff user-specific data into the `human` block (fragile, bleeds between users)
- Either way, you can't cleanly scope memory to a user

**With Identities:**

- One agent, many users
- Blocks bind to identities via `identity_ids`
- When a user interacts, the agent sees the blocks associated with that user's identity
- Other users' blocks stay isolated

This is the foundation for multi-tenant Letta deployments.

---

## API Reference

### List Identities

```
GET /v1/identities
```

Params: `limit`, `before`, `after`, `name`, `identifier_key`, `identity_type`, `project_id`.

### Get Identity

```
GET /v1/identities/{identity_id}
```

### Create Identity

```
POST /v1/identities
```

```json
{
  "name": "Clay",
  "identifier_key": "claydonjon@proton.me",
  "identity_type": "user",
  "block_ids": [],
  "properties": { "role": "admin", "joined_at": "2025-06-14" }
}
```

### Update Identity

```
PATCH /v1/identities/{identity_id}
```

Partial update. Common fields: `name`, `properties`, `block_ids`.

### Delete Identity

```
DELETE /v1/identities/{identity_id}
```

### Get or Create (idempotent)

Most SDKs expose a helper that creates if not exists, otherwise returns existing:

```python
identity = client.identities.upsert(
    identifier_key="claydonjon@proton.me",
    name="Clay",
    identity_type="user",
)
```

---

## Binding Blocks to Identities

Two ways:

### A. Create block with `identity_ids`

```python
client.blocks.create(
    label="human_preferences",
    value="Clay prefers terse responses. Likes Ryker-mode.",
    identity_ids=[clay_identity_id],
    limit=20000,
)
```

### B. Attach an existing block to an identity

```python
client.identities.blocks.attach(
    identity_id=clay_identity_id,
    block_id=existing_block_id,
)
```

Detach:

```python
client.identities.blocks.detach(
    identity_id=clay_identity_id,
    block_id=existing_block_id,
)
```

---

## Binding Agents to Identities

Agents can also bind to identities. An agent with an identity binding presents identity-scoped blocks to the model automatically:

```python
client.agents.create(
    name="support_agent",
    model="letta/kimi-k2.5",
    memory_blocks=[
        {"label": "persona", "value": "You are a support agent for the Donjon app."},
    ],
    identity_ids=[clay_identity_id],
)
```

When Clay's identity is active, the agent has his identity-bound blocks in context. When a different user's identity is active, it has theirs.

---

## Pattern: One Agent, Many Users

The simplest multi-tenant pattern:

```python
# 1. Create the agent once
support = client.agents.create(
    name="donjon_support",
    model="letta/kimi-k2.5",
    memory_blocks=[
        {"label": "persona", "value": "You help users with the Donjon app."},
    ],
    tools=[send_message_tool_id, knowledge_base_tool_id],
)

# 2. Per-user setup (on signup)
def setup_user(user_email: str, user_display_name: str):
    identity = client.identities.upsert(
        identifier_key=user_email,
        name=user_display_name,
        identity_type="user",
    )
    # Create a user-specific block
    user_block = client.blocks.create(
        label=f"human_{user_email}",
        value=f"The user is {user_display_name}.",
        limit=20000,
        identity_ids=[identity.id],
    )
    return identity.id

# 3. On each message, use the identity
def chat(user_email: str, message: str):
    identity = client.identities.retrieve_by_key(identifier_key=user_email)
    response = client.agents.messages.create(
        agent_id=support.id,
        messages=[{"role": "user", "content": message}],
        identity_id=identity.id,  # agent sees identity-scoped blocks
    )
    return response
```

---

## Pattern: Org-Level Scoping

For B2B tools where an agent serves a whole organization:

```python
# Create org identity
donjon_org = client.identities.upsert(
    identifier_key="org-donjon",
    name="Donjon Intelligence Systems",
    identity_type="org",
    properties={"plan": "enterprise", "agent_count_limit": 100},
)

# Create per-org org-standards block
client.blocks.create(
    label="org_standards",
    value="Donjon agents follow these standards: ...",
    identity_ids=[donjon_org.id],
)

# An agent scoped to this org sees org standards automatically
client.agents.create(
    name="donjon_ops_agent",
    model="letta/kimi-k2.5",
    identity_ids=[donjon_org.id],
)
```

An agent can have **both** a user and an org identity attached — it sees both scopes' blocks.

---

## Pattern: Properties as Runtime Feature Flags

The `properties` field is free-form JSON. Use it for:

- **Feature flags** — `{"beta_memory": true}`, read by tools at runtime
- **Quotas** — `{"max_messages_per_day": 1000}`, enforced by a custom tool
- **Preferences** — `{"language": "en", "timezone": "America/Chicago"}`
- **Audit trail hooks** — `{"last_compliance_check": "2026-04-23"}`

Retrieve properties in a tool:

```python
def my_tool(message: str) -> str:
    """Tool that respects user quota from identity properties."""
    import os
    from letta_client import Letta
    client = Letta(token=os.environ["LETTA_API_KEY"])
    # runtime context provides current identity ID
    identity = client.identities.retrieve(current_identity_id)
    quota = identity.properties.get("max_messages_per_day", 100)
    # enforce quota
    ...
```

(Tool runtime semantics vary by Letta version; confirm what context is available in your version.)

---

## Pattern: Identity Migration

When a user's email changes, or you're migrating from one auth system to another:

```python
# Option A: update identifier_key
client.identities.modify(
    identity_id=old_identity_id,
    identifier_key="new-email@example.com",
)

# Option B: create new identity, transfer block bindings, delete old
new_identity = client.identities.create(
    name=old_identity.name,
    identifier_key="new-email@example.com",
    identity_type="user",
)
for block_id in old_identity.block_ids:
    client.identities.blocks.attach(identity_id=new_identity.id, block_id=block_id)
    client.identities.blocks.detach(identity_id=old_identity_id, block_id=block_id)
client.identities.delete(identity_id=old_identity_id)
```

Option A is simpler. Option B is required if you need to preserve both identities (edge case).

---

## Pattern: Compliance — Identity Audit

Part of a compliance sweep — verify every active agent has the right identity bindings:

```python
def audit_identity_bindings():
    agents = list(client.agents.list(limit=100))
    for agent in agents:
        if not agent.identity_ids:
            print(f"⚠️  Agent {agent.name} has no identity bindings")
            continue
        for ident_id in agent.identity_ids:
            try:
                ident = client.identities.retrieve(ident_id)
                if ident.identity_type == "user" and not ident.identifier_key:
                    print(f"⚠️  Agent {agent.name} → identity {ident.name} has no identifier_key")
            except Exception as e:
                print(f"❌  Agent {agent.name} → stale identity {ident_id}: {e}")

audit_identity_bindings()
```

---

## Identity Anti-Patterns

- **Don't** put secrets in `properties`. It's not an encrypted vault — use your secret manager.
- **Don't** use `identity_type: "other"` as a catch-all. Define the type semantics explicitly in your system — a mixed-use `other` creates the same mess as an untyped tag.
- **Don't** skip Identities and stuff user context into the `human` block of a per-user agent. You lose the scaling benefits and pay per-agent costs unnecessarily.
- **Don't** forget to clean up. When a user deletes their account, delete the identity and (after retention) the associated blocks. Stale identities bloat lookups.

---

## Common Asks

### "Make my agent multi-tenant"

Refactor the per-user agent into: one shared agent + one identity per user + per-identity blocks. See "Pattern: One Agent, Many Users" above.

### "Let two users have different conversations with the same agent"

Identities handle this. Each message call passes the user's `identity_id`; the agent sees identity-scoped blocks for that user.

### "I want the agent to know who's an admin"

Put `{"role": "admin"}` in the identity's `properties` and have a tool or the persona block reference it at runtime.

### "I want to migrate from 500 per-user agents to one agent with identities"

1. List your per-user agents
2. Extract each agent's `human` block (that's your per-user state)
3. Create identities for each user
4. Create blocks bound to each identity with the extracted state
5. Create the single shared agent with the shared persona
6. Route messages through the shared agent with identity context
7. Deprecate the old per-user agents (keep for 30 days as rollback window)

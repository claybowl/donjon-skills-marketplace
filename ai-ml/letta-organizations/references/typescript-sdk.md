# TypeScript SDK (`@letta-ai/letta-client` / `letta-node`)

The TypeScript SDK mirrors the Python SDK with full feature parity — sync and async, streaming, all endpoints. Use it for Next.js apps, Node services, Electron apps, and browser contexts where you proxy through a backend.

Upstream: [github.com/letta-ai/letta-node](https://github.com/letta-ai/letta-node)
Vercel AI SDK provider: [github.com/letta-ai/vercel-ai-sdk-provider](https://github.com/letta-ai/vercel-ai-sdk-provider)
SDK announcement: [letta.com/blog/announcing-our-sdks](https://www.letta.com/blog/announcing-our-sdks)

---

## Install

```sh
npm install @letta-ai/letta-client
# or
pnpm add @letta-ai/letta-client
# or
yarn add @letta-ai/letta-client
```

---

## Client Setup

```ts
import { LettaClient } from "@letta-ai/letta-client";

const client = new LettaClient({
  token: process.env.LETTA_API_KEY!,
  // baseUrl: "http://localhost:8283", // for self-hosted
});
```

**Never ship the API key to the browser.** If you're building a web app, proxy calls through your backend (Next.js API route, Express endpoint, Cloudflare Worker, etc.). The SDK is isomorphic but the token is not.

---

## Agents

```ts
// List
const agents = await client.agents.list({ limit: 50 });

// Paginate
async function listAllAgents() {
  const all = [];
  let cursor: string | undefined;
  while (true) {
    const batch = await client.agents.list({ limit: 100, after: cursor });
    all.push(...batch);
    if (batch.length < 100) break;
    cursor = batch[batch.length - 1].id;
  }
  return all;
}

// Retrieve
const agent = await client.agents.retrieve(agentId);

// Create
const agent = await client.agents.create({
  name: "support_agent",
  description: "Handles support tickets",
  model: "letta/kimi-k2.5",
  embeddingModel: "text-embedding-ada-002",
  tags: ["donjon", "support"],
  memoryBlocks: [
    { label: "persona", value: "You handle support for the Donjon app.", limit: 20000 },
    { label: "human", value: "", limit: 20000 },
  ],
  tools: ["tool-id-1", "tool-id-2"],
  enableSleeptime: true,
  sleeptimeAgentFrequency: 5,
});

// Update
await client.agents.modify(agentId, {
  model: "openai/gpt-4o-mini",  // model swap
  tags: ["donjon", "support", "v2"],
});

// Delete
await client.agents.delete(agentId);

// Export / Import
const exported = await client.agents.export(agentId);
const restored = await client.agents.importAgent({ body: exported });
```

---

## Messages

### Sync

```ts
const response = await client.agents.messages.create(agentId, {
  messages: [{ role: "user", content: "Your task here" }],
  maxSteps: 50,
});

for (const msg of response.messages) {
  if (msg.messageType === "assistant_message") {
    console.log(msg.content);
  } else if (msg.messageType === "tool_call_message") {
    console.log(`Tool: ${msg.toolCall?.name}`);
  }
}
```

### Streaming (SSE)

```ts
const stream = await client.agents.messages.createStream(agentId, {
  messages: [{ role: "user", content: "Your task here" }],
  streamTokens: true,  // token-level
  // streamSteps: true, // step-level (coarser, less chatty)
});

for await (const event of stream) {
  if (event.messageType === "assistant_message") {
    process.stdout.write(event.content ?? "");
  }
}
```

### List history

```ts
const messages = await client.agents.messages.list(agentId, { limit: 50 });
```

---

## Memory Blocks

```ts
// List
const blocks = await client.agents.blocks.list(agentId);

// Retrieve specific
const persona = await client.agents.blocks.retrieve(agentId, "persona");

// Modify
await client.agents.blocks.modify(agentId, "persona", {
  value: "New persona text",
});

// Create custom
await client.agents.blocks.create(agentId, {
  label: "current_tasks",
  value: "- Task 1\n- Task 2",
  limit: 20000,
  description: "Active tasks",
});

// Delete
await client.agents.blocks.delete(agentId, "current_tasks");

// Attach a shared block
await client.agents.blocks.attach(agentId, { id: sharedBlockId });

// Detach
await client.agents.blocks.detach(agentId, sharedBlockId);
```

---

## Tools

```ts
// List org-wide tools
const tools = await client.tools.list();

// Create a custom tool
const tool = await client.tools.create({
  name: "my_tool",
  description: "What this does",
  sourceCode: `def my_tool(param: str) -> str:
    '''docstring'''
    return f"got: {param}"`,
  tags: ["custom"],
});

// Attach to agent
await client.agents.tools.attach(agentId, { toolId: tool.id });

// Detach
await client.agents.tools.detach(agentId, { toolId: tool.id });

// Agent's current tool list
const agentTools = await client.agents.tools.list(agentId);
```

---

## Archival & Conversation Memory

```ts
// Insert archival memory
await client.agents.archivalMemory.insert(agentId, {
  text: "Important fact to remember",
});

// Search archival
const results = await client.agents.archivalMemory.search(agentId, {
  query: "semantic query",
  limit: 10,
});

// Search conversation history
const matches = await client.agents.conversationSearch.search(agentId, {
  query: "something user said earlier",
});
```

---

## Identities

```ts
const identity = await client.identities.create({
  name: "Clay",
  identifierKey: "claydonjon@proton.me",
  identityType: "user",
  properties: { role: "admin" },
});

// Upsert (create if not exists)
const identity = await client.identities.upsert({
  identifierKey: "claydonjon@proton.me",
  name: "Clay",
  identityType: "user",
});

// Bind a block
await client.blocks.create({
  label: "human_preferences",
  value: "Clay prefers terse responses.",
  identityIds: [identity.id],
});

// Use identity in a message call
await client.agents.messages.create(agentId, {
  messages: [{ role: "user", content: "Hi" }],
  identityId: identity.id,
});
```

See `identities.md` for deeper patterns.

---

## Groups

```ts
const group = await client.groups.create({
  managerType: "supervisor",
  managerAgentId: supervisorId,
  agentIds: [workerAId, workerBId],
});

const response = await client.groups.messages.create(group.id, {
  messages: [{ role: "user", content: "Research and write a brief" }],
});

// Stream
const stream = await client.groups.messages.createStream(group.id, {
  messages: [{ role: "user", content: "Start the debate" }],
});
for await (const event of stream) {
  console.log(event);
}
```

See `groups.md` for manager type patterns.

---

## Vercel AI SDK Integration

The [Vercel AI SDK provider](https://github.com/letta-ai/vercel-ai-sdk-provider) lets you use Letta agents as providers in any Vercel-AI-SDK app (Next.js, Remix, SvelteKit, etc.):

```sh
npm install @letta-ai/vercel-ai-sdk-provider ai
```

```ts
// app/api/chat/route.ts (Next.js App Router)
import { streamText } from "ai";
import { letta } from "@letta-ai/vercel-ai-sdk-provider";

export async function POST(req: Request) {
  const { messages, agentId } = await req.json();

  const result = await streamText({
    model: letta(agentId, {
      apiKey: process.env.LETTA_API_KEY!,
    }),
    messages,
  });

  return result.toDataStreamResponse();
}
```

```tsx
// app/chat/page.tsx
"use client";
import { useChat } from "ai/react";

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit } = useChat({
    api: "/api/chat",
    body: { agentId: "agent-abc123" },
  });

  return (
    <div>
      {messages.map((m) => (
        <div key={m.id}>
          <strong>{m.role}:</strong> {m.content}
        </div>
      ))}
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} />
      </form>
    </div>
  );
}
```

This gives you a Letta-backed stateful agent with memory in a standard `useChat` interface. The agent's memory persists across requests automatically.

---

## Common TypeScript Patterns

### Paginate everything into an array

```ts
async function fetchAll<T>(
  fetcher: (args: { limit: number; after?: string }) => Promise<T[]>,
  pageSize = 100,
): Promise<T[]> {
  const all: T[] = [];
  let cursor: string | undefined;
  while (true) {
    const batch = await fetcher({ limit: pageSize, after: cursor });
    all.push(...batch);
    if (batch.length < pageSize) break;
    // @ts-expect-error — assumes items have an `id`
    cursor = batch[batch.length - 1].id;
  }
  return all;
}

const agents = await fetchAll((args) => client.agents.list(args));
```

### Bulk persona update with diff + confirm

```ts
import { diffChars } from "diff";

async function sweepPersonas(tagFilter: string, updater: (old: string) => string) {
  const agents = await client.agents.list({ tags: [tagFilter], limit: 200 });
  const changes: Array<{ name: string; id: string; before: string; after: string }> = [];

  for (const agent of agents) {
    const persona = await client.agents.blocks.retrieve(agent.id, "persona");
    const oldValue = persona.value ?? "";
    const newValue = updater(oldValue);
    if (oldValue === newValue) continue;
    changes.push({ name: agent.name, id: agent.id, before: oldValue, after: newValue });
  }

  console.log(`Preview: ${changes.length} agents would change`);
  for (const c of changes) {
    console.log(`--- ${c.name} ---`);
    for (const part of diffChars(c.before, c.after)) {
      const sigil = part.added ? "+" : part.removed ? "-" : " ";
      console.log(`${sigil} ${part.value.slice(0, 80)}`);
    }
  }

  // Require confirmation
  if (!process.env.APPLY) {
    console.log("\nRe-run with APPLY=1 to commit.");
    return;
  }

  for (const c of changes) {
    await client.agents.blocks.modify(c.id, "persona", { value: c.after });
    console.log(`✓ ${c.name}`);
  }
}

await sweepPersonas("donjon", (p) => p.replace(/old phrase/g, "new phrase"));
```

### Listen to a run via SSE

```ts
const stream = await client.agents.messages.createStream(agentId, {
  messages: [{ role: "user", content: "Do the thing" }],
  streamTokens: true,
});

for await (const event of stream) {
  switch (event.messageType) {
    case "reasoning_message":
      // internal chain-of-thought; usually hidden from UI
      break;
    case "tool_call_message":
      console.log(`🛠  ${event.toolCall?.name}(${event.toolCall?.arguments})`);
      break;
    case "tool_return_message":
      console.log(`↩  ${event.toolReturn}`);
      break;
    case "assistant_message":
      process.stdout.write(event.content ?? "");
      break;
    case "stop_reason":
      console.log(`\n⏹  ${event.stopReason}`);
      break;
  }
}
```

### Hono / Elysia / Express proxy pattern

Put the Letta client on the server side and expose only the message endpoint:

```ts
// server.ts (Hono)
import { Hono } from "hono";
import { LettaClient } from "@letta-ai/letta-client";
import { streamSSE } from "hono/streaming";

const app = new Hono();
const letta = new LettaClient({ token: process.env.LETTA_API_KEY! });

app.post("/agent/:id/chat", (c) => {
  const agentId = c.req.param("id");
  return streamSSE(c, async (sse) => {
    const { messages } = await c.req.json();
    const stream = await letta.agents.messages.createStream(agentId, {
      messages,
      streamTokens: true,
    });
    for await (const event of stream) {
      await sse.writeSSE({ event: event.messageType, data: JSON.stringify(event) });
    }
  });
});
```

The browser only sees your own endpoint. Letta API key stays on the server.

---

## TypeScript-specific Tips

- All SDK types are exported. Use `import type { Agent, Block, Message, Group, Identity } from "@letta-ai/letta-client";` for strong typing.
- The SDK uses camelCase in TypeScript; the REST API uses snake_case in JSON. The client handles the conversion.
- For Next.js Server Actions, wrap Letta calls in server-only files and use them from client components via `use server` directives.
- For Electron, use the SDK in the main process only; never expose the Letta token via IPC.
- For Cloudflare Workers, the SDK works in the worker runtime — just make sure `fetch` is available (it is, globally).

---

## When To Use Python vs TypeScript

Go Python for:
- Scripts, CLIs, data pipelines
- Custom tool authoring (Letta tools are typically Python)
- Jupyter notebook exploration
- Integration with ML/data-science stacks

Go TypeScript for:
- Web frontends (via proxy)
- Next.js / Remix / SvelteKit apps
- Edge/serverless (Cloudflare, Vercel, Deno)
- Electron / desktop apps
- Donjon-paperclip / Doer UI integration

For Clay's fork specifically: the Doer UI is TS, the Doer server is TS, and any plugin UI that talks to Letta should use `@letta-ai/letta-client` on the worker side (not the UI — follow the Paperclip bridge pattern).

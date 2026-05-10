# Excalidraw Vibe Planning Skill

Visual brainstorming and architecture design using Excalidraw MCP server.

## Quick Start

```bash
# 1. Start the canvas server
docker run -d -p 3000:3000 --name mcp-excalidraw-canvas ghcr.io/yctimlin/mcp_excalidraw-canvas:latest

# 2. Open browser to verify
curl http://localhost:3000
```

## Usage

Mention any of these phrases to activate:
- "vibe plan" or "vibe planning"
- "brainstorm architecture" or "architecture diagram"
- "draw out" or "sketch out" system design
- "let's diagram" or "visualize this"
- "excalidraw session" or "whiteboard this"

## Examples

**Brainstorming a new system:**
```
User: "I want to build a real-time chat app. Let's vibe plan it!"
```

**Refactoring existing architecture:**
```
User: "We need to migrate from monolith to microservices. Can you diagram an approach?"
```

**Exploring integrations:**
```
User: "I want to add AI features to our platform. Let's sketch out the architecture."
```

## Configuration

Ensure your `.opencode/mcp-config.json` includes:

```json
{
  "mcpServers": {
    "excalidraw": {
      "type": "local",
      "command": ["docker", "run", "-i", "--rm", "-e", "EXPRESS_SERVER_URL=http://host.docker.internal:3000", "-e", "ENABLE_CANVAS_SYNC=true", "ghcr.io/yctimlin/mcp_excalidraw:latest"],
      "enabled": true
    }
  }
}
```

## Status

✅ Canvas server running  
✅ MCP server configured  
✅ Ready to brainstorm

View canvas: http://localhost:3000

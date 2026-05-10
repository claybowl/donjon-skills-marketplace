# Pieces MCP Skill for OpenCode

Access your Pieces Long-Term Memory directly from OpenCode.

## Quick Start

### Option 1: Direct Python Query (Recommended)

Query Pieces LTM directly without setting up the full MCP skill:

```bash
# Query yesterday's activity
python .opencode/skills/pieces-mcp/query_pieces.py "What did I do yesterday on February 7, 2026?"

# Search for specific topics
python .opencode/skills/pieces-mcp/query_pieces.py "Show me React code snippets I saved"

# List recent snippets
python .opencode/skills/pieces-mcp/query_pieces.py --snippets
```

### Option 2: MCP Server Mode

Run as a proper MCP server for integration with OpenCode:

```bash
# Install dependencies
pip install -r .opencode/skills/pieces-mcp/requirements.txt

# Run the server
python .opencode/skills/pieces-mcp/server.py
```

Then use in OpenCode:
```
Use the ask_pieces_ltm tool to find what I worked on yesterday
```

## What You Can Query

**Activity History:**
- "What did I code yesterday?"
- "What files did I work on February 7, 2026?"
- "Show me my work from last week"

**Code Snippets:**
- "Find my saved Python functions"
- "Show snippets from yesterday"
- "Search for authentication code"

**Context & Memory:**
- "What was I debugging yesterday?"
- "Show me conversations from my last meeting"
- "What dependencies did I discuss?"

## Requirements

1. **PiecesOS Installed and Running**
   - Download from: https://code.pieces.app/
   - Must be running in the background

2. **MCP Server Enabled**
   - Open Pieces Desktop App
   - Go to Settings > Extensions > MCP
   - Enable "MCP Server"

3. **Python Dependencies**
   ```bash
   pip install mcp httpx
   ```

## Troubleshooting

**"Cannot connect to Pieces MCP server"**
- Verify PiecesOS is running (check system tray)
- Check Pieces Desktop > Settings > MCP is enabled
- Try restarting PiecesOS

**"404 Not Found" or "400 Bad Request"**
- The endpoint URL may differ by Pieces version
- Check Pieces settings for the exact MCP URL
- Default: `http://localhost:39300/model_context_protocol/2025-03-26/mcp`

**"Failed to extract context"**
- Pieces LTM needs time to index your activity
- Ensure Pieces Desktop or IDE extension is actively running
- Some data may take hours to appear in LTM

**No results for specific dates**
- Pieces LTM captures what it can see
- Browser activity, IDE usage, and Desktop app usage are tracked
- Make sure Pieces extensions are installed in your browsers/IDEs

## Files

- `SKILL.md` - Full documentation
- `server.py` - MCP server implementation
- `query_pieces.py` - Direct query script (easiest to use)
- `pieces_client.py` - Proper MCP client using SSE transport
- `requirements.txt` - Python dependencies
- `skill.json` - OpenCode skill configuration

## How It Works

1. **PiecesOS** runs locally and captures your workflow
2. **LTM-2.7** (Long-Term Memory) indexes and enriches the data
3. **MCP Server** exposes tools to query this memory
4. **This Skill** connects to the MCP server and provides:
   - `ask_pieces_ltm` - Natural language queries
   - `list_recent_snippets` - Saved code
   - `search_snippets` - Find specific code

## Next Steps

Try these queries:
```bash
python .opencode/skills/pieces-mcp/query_pieces.py "What did I do yesterday?"
python .opencode/skills/pieces-mcp/query_pieces.py "Show me code from February 7"
python .opencode/skills/pieces-mcp/query_pieces.py "What was my last project about?"
```

For more info: https://docs.pieces.app/products/mcp/get-started

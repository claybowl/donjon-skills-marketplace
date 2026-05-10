#!/usr/bin/env python3
"""
Pieces MCP Skill Wrapper
Connects to local Pieces MCP server to query Long-Term Memory
"""

import asyncio
import json
import sys
from typing import Any
from urllib.parse import urljoin

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Pieces MCP server endpoint
PIECES_MCP_URL = "http://localhost:39300/model_context_protocol/2025-03-26/mcp"

app = Server("pieces-mcp-skill")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for querying Pieces LTM."""
    return [
        Tool(
            name="ask_pieces_ltm",
            description="Query your Pieces Long-Term Memory for context about your work history, coding activity, and saved snippets. Returns natural language summaries of your activity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language question about your activity. Examples: 'What did I do yesterday?', 'Show me code snippets I saved last week', 'What files did I edit on February 7, 2026?'"
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Optional time period to narrow search (e.g., 'yesterday', 'last week', 'February 7, 2026')"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="list_recent_snippets",
            description="Get recently saved code snippets from your Pieces library.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of snippets to return (default: 10)",
                        "default": 10
                    },
                    "date_filter": {
                        "type": "string",
                        "description": "Optional date filter in YYYY-MM-DD format (e.g., '2026-02-07')"
                    }
                }
            }
        ),
        Tool(
            name="search_snippets",
            description="Search your saved code snippets by keywords or language.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search terms to find relevant snippets"
                    },
                    "language": {
                        "type": "string",
                        "description": "Optional programming language filter (e.g., 'python', 'javascript', 'typescript')"
                    }
                },
                "required": ["query"]
            }
        )
    ]

async def call_pieces_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """Call a tool on the Pieces MCP server via HTTP."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Pieces MCP uses JSON-RPC style communication
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": 1
            }
            
            response = await client.post(
                f"{PIECES_MCP_URL}/tools/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            return {
                "error": f"Cannot connect to Pieces MCP server at {PIECES_MCP_URL}. Ensure PiecesOS is running and MCP is enabled."
            }
        except Exception as e:
            return {"error": f"Error calling Pieces MCP: {str(e)}"}

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls by forwarding to Pieces MCP server."""
    
    if name == "ask_pieces_ltm":
        query = arguments.get("query", "")
        time_range = arguments.get("time_range", "")
        
        # Enhance query with time range if provided
        if time_range:
            query = f"{query} (time range: {time_range})"
        
        # Call the actual Pieces MCP ask_pieces_ltm tool
        result = await call_pieces_mcp_tool("ask_pieces_ltm", {"query": query})
        
        if "error" in result:
            return [TextContent(type="text", text=f"❌ Error: {result['error']}")]
        
        # Extract and format the response
        content = result.get("result", {}).get("content", [])
        if content:
            text = content[0].get("text", "No results found in Pieces LTM.")
            return [TextContent(type="text", text=text)]
        else:
            return [TextContent(type="text", text="No activity found in Pieces LTM for the specified query.")]
    
    elif name == "list_recent_snippets":
        limit = arguments.get("limit", 10)
        date_filter = arguments.get("date_filter", "")
        
        result = await call_pieces_mcp_tool("list_recent_snippets", {
            "limit": limit,
            "date_filter": date_filter
        })
        
        if "error" in result:
            return [TextContent(type="text", text=f"❌ Error: {result['error']}")]
        
        snippets = result.get("result", {}).get("snippets", [])
        if not snippets:
            return [TextContent(type="text", text="No snippets found.")]
        
        text = f"📎 Recent Snippets ({len(snippets)} found):\n\n"
        for i, snippet in enumerate(snippets, 1):
            text += f"{i}. **{snippet.get('title', 'Untitled')}**\n"
            text += f"   Language: {snippet.get('language', 'Unknown')}\n"
            text += f"   Saved: {snippet.get('saved_at', 'Unknown date')}\n\n"
        
        return [TextContent(type="text", text=text)]
    
    elif name == "search_snippets":
        query = arguments.get("query", "")
        language = arguments.get("language", "")
        
        result = await call_pieces_mcp_tool("search_snippets", {
            "query": query,
            "language": language
        })
        
        if "error" in result:
            return [TextContent(type="text", text=f"❌ Error: {result['error']}")]
        
        snippets = result.get("result", {}).get("snippets", [])
        if not snippets:
            return [TextContent(type="text", text=f"No snippets found matching '{query}'.")]
        
        text = f"🔍 Search Results for '{query}' ({len(snippets)} found):\n\n"
        for i, snippet in enumerate(snippets, 1):
            text += f"{i}. **{snippet.get('title', 'Untitled')}**\n"
            text += f"   Language: {snippet.get('language', 'Unknown')}\n"
            text += f"   Preview: {snippet.get('preview', 'No preview')[:100]}...\n\n"
        
        return [TextContent(type="text", text=text)]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

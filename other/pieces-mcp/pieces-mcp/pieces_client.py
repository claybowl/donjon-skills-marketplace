#!/usr/bin/env python3
"""
Pieces MCP Client using proper MCP protocol
Connects via HTTP SSE transport
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta

from mcp import ClientSession
from mcp.client.sse import sse_client

PIECES_MCP_URL = "http://localhost:39300/model_context_protocol/2025-11-25/mcp"

async def query_pieces_ltm(question: str):
    """Query Pieces LTM using proper MCP client."""
    try:
        async with sse_client(PIECES_MCP_URL) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the session
                await session.initialize()
                
                # List available tools
                tools_response = await session.list_tools()
                print(f"Available tools: {[tool.name for tool in tools_response.tools]}")
                
                # Call ask_pieces_ltm tool
                result = await session.call_tool(
                    "ask_pieces_ltm",
                    {"query": question}
                )
                
                return {"success": True, "result": result}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

async def main():
    """Main function."""
    if len(sys.argv) < 2:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%B %d, %Y")
        query = f"What did I do yesterday on {yesterday}?"
    else:
        query = " ".join(sys.argv[1:])
    
    print(f"Querying Pieces LTM: {query}\n")
    response = await query_pieces_ltm(query)
    
    if "error" in response:
        print(f"Error: {response['error']}")
        print("\nTroubleshooting:")
        print("1. Ensure PiecesOS is running")
        print("2. Enable MCP in Pieces settings")
        print("3. Verify the URL matches your Pieces version")
        print(f"   Current URL: {PIECES_MCP_URL}")
    else:
        print("Result:")
        result = response.get("result")
        if result:
            print(json.dumps(result, indent=2, default=str))
        else:
            print("No result returned")

if __name__ == "__main__":
    asyncio.run(main())

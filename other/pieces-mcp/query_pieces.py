#!/usr/bin/env python3
"""
Direct Pieces MCP Query Tool
Simple script to query Pieces LTM without full MCP protocol
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta

import httpx

PIECES_MCP_URL = "http://localhost:39300/model_context_protocol/2025-03-26/mcp"

async def ask_pieces_ltm(query: str) -> dict:
    """Directly query Pieces LTM through the MCP server."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Try the tools/list endpoint first to verify connection
            response = await client.get(f"{PIECES_MCP_URL}/tools/list")
            print(f"Tools list status: {response.status_code}")
            if response.status_code == 200:
                print(f"Available tools: {response.text[:500]}")
        except Exception as e:
            print(f"Tools list error: {e}")
        
        # Now try to call ask_pieces_ltm
        try:
            payload = {
                "name": "ask_pieces_ltm",
                "arguments": {
                    "query": query
                }
            }
            
            response = await client.post(
                f"{PIECES_MCP_URL}/tools/call",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

async def main():
    """Main function."""
    if len(sys.argv) < 2:
        # Default query for yesterday
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%B %d, %Y")
        query = f"What did I do yesterday on {yesterday}?"
    else:
        query = " ".join(sys.argv[1:])
    
    print(f"Querying Pieces LTM: {query}\n")
    result = await ask_pieces_ltm(query)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        print(f"\nMake sure:")
        print("1. PiecesOS is running")
        print("2. MCP server is enabled in Pieces settings")
        print(f"3. The MCP endpoint is accessible at {PIECES_MCP_URL}")
    else:
        print("Result:")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())

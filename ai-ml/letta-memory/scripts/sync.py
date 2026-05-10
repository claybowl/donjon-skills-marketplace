#!/usr/bin/env python3
"""
DonDog Letta Memory Sync Script

Syncs .letta/ memory files to/from Letta Cloud memory blocks.

Usage:
    python sync_to_letta.py      # Push .letta/ files to Letta
    python sync_from_letta.py    # Pull Letta blocks to .letta/ files
"""

import os
import json
from letta_client import Letta

# Configuration
LETTA_API_KEY = os.getenv("LETTA_API_KEY", "")
LETTA_BASE_URL = os.getenv("LETTA_BASE_URL", "http://localhost:8283/v1")

# Map .letta/ files to Letta block labels
FILE_TO_BLOCK = {
    ".letta/work/persona.md": "persona",
    ".letta/work/human.md": "human",
    ".letta/system/context/projects.md": "knowledge_projects",
    ".letta/system/context/tech.md": "knowledge_tech",
    ".letta/system/goals/current.md": "goals",
    ".letta/work/active.md": "active_task",
    ".letta/work/notes.md": "notes",
}


def get_client():
    """Initialize Letta client."""
    if not LETTERA_API_KEY:
        raise ValueError("LETTA_API_KEY environment variable not set")

    return Letta(api_key=LETTA_API_KEY, base_url=LETTA_BASE_URL)


def sync_to_letta(agent_id: str):
    """Push .letta/ files to Letta memory blocks."""
    client = get_client()

    for file_path, block_label in FILE_TO_BLOCK.items():
        if not os.path.exists(file_path):
            print(f"Skipping {file_path} (not found)")
            continue

        with open(file_path) as f:
            content = f.read()

        try:
            client.agents.blocks.update(
                agent_id=agent_id, block_label=block_label, value=content
            )
            print(f"✓ Updated {block_label} from {file_path}")
        except Exception as e:
            print(f"✗ Failed to update {block_label}: {e}")


def sync_from_letta(agent_id: str):
    """Pull Letta memory blocks to .letta/ files."""
    client = get_client()

    blocks = client.agents.blocks.list(agent_id=agent_id)
    block_map = {block.label: block.value for block in blocks}

    for file_path, block_label in FILE_TO_BLOCK.items():
        if block_label not in block_map:
            print(f"Skipping {block_label} (not in Letta)")
            continue

        content = block_map[block_label]

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            f.write(content)

        print(f"✓ Saved {block_label} to {file_path}")


def create_agent_with_memory():
    """Create a new Letta agent with .letta/ files as memory."""
    client = get_client()

    # Load memory files
    memory_blocks = []

    if os.path.exists(".letta/work/persona.md"):
        with open(".letta/work/persona.md") as f:
            memory_blocks.append({"label": "persona", "value": f.read(), "limit": 5000})

    if os.path.exists(".letta/work/human.md"):
        with open(".letta/work/human.md") as f:
            memory_blocks.append({"label": "human", "value": f.read(), "limit": 5000})

    if not memory_blocks:
        print("No memory files found in .letta/")
        return

    # Create agent
    agent = client.agents.create(
        name="DonDog",
        memory_blocks=memory_blocks,
        model="openai/gpt-4o-mini",
        embedding="openai/text-embedding-3-small",
    )

    print(f"✓ Created agent: {agent.id}")
    print(f"  Name: {agent.name}")
    print(f"  Memory blocks: {len(memory_blocks)}")

    return agent


def list_agent_memory(agent_id: str):
    """List all memory blocks for an agent."""
    client = get_client()

    blocks = client.agents.blocks.list(agent_id=agent_id)

    print(f"Memory blocks for agent {agent_id}:")
    print("-" * 40)
    for block in blocks:
        print(f"\n[{block.label}]")
        print(f"  Size: {len(block.value)}/{block.limit} chars")
        print(f"  Preview: {block.value[:100]}...")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print(
            "  python sync_to_letta.py create          # Create Letta agent from .letta/"
        )
        print("  python sync_to_letta.py sync <agent-id> # Push .letta/ to Letta")
        print("  python sync_to_letta.py pull <agent-id> # Pull Letta to .letta/")
        print("  python sync_to_letta.py list <agent-id> # List memory blocks")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create":
        create_agent_with_memory()
    elif command == "sync" and len(sys.argv) > 2:
        sync_to_letta(sys.argv[2])
    elif command == "pull" and len(sys.argv) > 2:
        sync_from_letta(sys.argv[2])
    elif command == "list" and len(sys.argv) > 2:
        list_agent_memory(sys.argv[2])
    else:
        print("Unknown command")
        sys.exit(1)

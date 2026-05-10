#!/usr/bin/env python3
"""
Scaffold a starter question bank for a custom trait model.

Doesn't write the actual item text — Claude (or you) does that. This script
sets up the structure: the right number of slots per trait, polarity mix,
ID conventions, and a TODO marker on each item.

Usage:
    python generate_question_bank.py \\
        --traits conscientiousness need_for_cognition agency_motivation \\
        --items-per-trait 5 \\
        --output question_bank.json \\
        [--scale likert_7] \\
        [--name "My Personality Test"]

Output is a `question_bank.json` matching the schema used by score_test.py.
Polarity is alternated direct/reverse so each trait has a balanced mix.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def short_code(trait: str) -> str:
    """First 3 letters of each underscore-separated word, uppercase. Trim to 3."""
    parts = trait.split("_")
    if len(parts) == 1:
        return parts[0][:3].upper()
    return "".join(p[0] for p in parts).upper()[:3]


def build_bank(
    traits: list[str],
    items_per_trait: int,
    scale: str,
    name: str,
) -> dict:
    items = []
    for trait in traits:
        code = short_code(trait)
        for i in range(items_per_trait):
            polarity = 1 if i % 2 == 0 else -1
            items.append({
                "id": f"Q-{code}-{i + 1:02d}",
                "text": f"TODO: write a {'direct' if polarity == 1 else 'reverse-scored'} item for {trait}.",
                "primary_trait": trait,
                "secondary_trait": None,
                "polarity": polarity,
                "status": "draft"
            })

    anchors_for = {
        "likert_5": {"1": "Strongly Disagree", "3": "Neutral", "5": "Strongly Agree"},
        "likert_7": {"1": "Strongly Disagree", "4": "Neutral", "7": "Strongly Agree"},
    }
    return {
        "$schema": "https://donjon.agency/schemas/personality-architect/question-bank-v1.json",
        "metadata": {
            "name": name,
            "version": "0.1.0",
            "scale": scale,
            "anchors": anchors_for.get(scale, {}),
            "trait_model": traits,
        },
        "items": items,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--traits", nargs="+", required=True, help="Trait names (snake_case)")
    p.add_argument("--items-per-trait", type=int, default=5)
    p.add_argument("--output", required=True, help="Path to write the JSON")
    p.add_argument("--scale", default="likert_7", choices=["likert_5", "likert_7"])
    p.add_argument("--name", default="Personality Test")
    args = p.parse_args()

    bank = build_bank(args.traits, args.items_per_trait, args.scale, args.name)
    Path(args.output).write_text(json.dumps(bank, indent=2))
    print(f"Wrote {args.output} — {len(bank['items'])} items across {len(args.traits)} traits.", file=sys.stderr)
    print(f"Each item has TODO text — fill them in following references/question-construction.md.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

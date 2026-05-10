#!/usr/bin/env python3
"""
Calibration check — simulate random respondents and verify the scorer
produces an approximately uniform distribution over archetypes.

A scorer that is biased toward one archetype on random input is biased
on real input too. Failing this check means the scoring is broken.

Usage:
    python calibration_check.py \\
        --question-bank question_bank.json \\
        --scoring-config scoring.json \\
        --tier 1 \\
        [--n 10000] \\
        [--seed 42] \\
        [--output calibration_report.json]

Pass criterion: for K archetypes, no archetype frequency should fall
outside [0.5/K, 1.5/K]. The script reports per-archetype frequency,
deviation from uniform, and an overall pass/fail.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from collections import Counter
from pathlib import Path

# Import the scorers from the same directory
sys.path.insert(0, str(Path(__file__).parent))
from score_test import score_tier_1, score_tier_2, load_json  # noqa: E402


def random_response(scale_min: int, scale_max: int) -> int:
    return random.randint(scale_min, scale_max)


def simulate(
    bank: dict,
    config: dict,
    tier: int,
    n: int,
) -> Counter:
    items = bank["items"]
    scale_min = config["scale"]["min"]
    scale_max = config["scale"]["max"]
    scorer = score_tier_1 if tier == 1 else score_tier_2

    primary_counts: Counter = Counter()
    for _ in range(n):
        responses = [
            {"question_id": item["id"], "response": random_response(scale_min, scale_max)}
            for item in items
        ]
        result = scorer(responses, bank, config)
        primary_counts[result["primary_archetype"]] += 1

    return primary_counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--question-bank", required=True)
    parser.add_argument("--scoring-config", required=True)
    parser.add_argument("--tier", type=int, choices=[1, 2], default=1)
    parser.add_argument("--n", type=int, default=10000, help="Number of simulated respondents")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--output", help="Optional JSON report path")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    bank = load_json(args.question_bank)
    config = load_json(args.scoring_config)

    archetypes = list(config["archetypes"].keys())
    counts = simulate(bank, config, args.tier, args.n)

    # Fill in zero counts for archetypes that never appeared
    for a in archetypes:
        counts.setdefault(a, 0)

    k = len(archetypes)
    expected = args.n / k if k else 0
    lower_bound = 0.5 / k
    upper_bound = 1.5 / k

    rows = []
    failures = []
    for a in archetypes:
        freq = counts[a] / args.n if args.n else 0
        deviation = freq - 1 / k
        ok = lower_bound <= freq <= upper_bound
        rows.append({
            "archetype": a,
            "count": counts[a],
            "frequency": round(freq, 4),
            "deviation_from_uniform": round(deviation, 4),
            "within_bounds": ok,
        })
        if not ok:
            failures.append(a)

    overall_pass = len(failures) == 0

    # Quick stats
    freqs = [r["frequency"] for r in rows]
    summary = {
        "n_respondents": args.n,
        "n_archetypes": k,
        "expected_frequency_per_archetype": round(1 / k, 4) if k else 0,
        "lower_bound_50pct": round(lower_bound, 4),
        "upper_bound_150pct": round(upper_bound, 4),
        "min_frequency": min(freqs) if freqs else 0,
        "max_frequency": max(freqs) if freqs else 0,
        "stddev": round(statistics.pstdev(freqs), 4) if freqs else 0,
        "failures": failures,
        "overall_pass": overall_pass,
    }

    report = {"per_archetype": rows, "summary": summary, "tier": args.tier}

    out = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(out)
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(out)

    # Also print a human-readable verdict to stderr
    if overall_pass:
        print(f"\n✓ Calibration PASS — all {k} archetypes within ±50% of uniform.", file=sys.stderr)
    else:
        print(f"\n✗ Calibration FAIL — {len(failures)} archetypes outside bounds: {', '.join(failures)}", file=sys.stderr)
        print("  Common fixes (try in order):", file=sys.stderr)
        print("    1. Mean-center your archetype signatures (subtract the per-trait", file=sys.stderr)
        print("       average across all archetypes from each signature).", file=sys.stderr)
        print("    2. Confirm score_test.py is using cosine similarity, not squared", file=sys.stderr)
        print("       distance (squared distance heavily biases toward archetypes", file=sys.stderr)
        print("       closest to origin under random input).", file=sys.stderr)
        print("    3. Audit polarity flags on every item — a single missed reverse", file=sys.stderr)
        print("       score can shift the calibration noticeably.", file=sys.stderr)
        print("    4. Check items-per-trait balance — uneven coverage biases the", file=sys.stderr)
        print("       trait vector, which biases the archetype distribution.", file=sys.stderr)
        print("  See references/validation.md and references/scoring.md.", file=sys.stderr)
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())

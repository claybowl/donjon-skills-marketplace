#!/usr/bin/env python3
"""
Reference scorer for personality-architect tests.

Implements:
  Tier 1 — weighted sum with poor-person ERS correction (per-user z-score)
  Tier 2 — Bayesian trait inference with explicit ERS latent variable
            (closed-form Kalman-style updates with Normal priors)

Tier 3 (adaptive question selection) is documented in references/scoring.md
but not implemented here — adaptive scoring requires real-time integration
with question-selection and is a different shape of program.

Usage:
    python score_test.py \\
        --question-bank question_bank.json \\
        --scoring-config scoring.json \\
        --responses responses.json \\
        --tier 1 \\
        [--output result.json]

If --output is omitted the result is printed to stdout.

Response file shape:
    [
      {"question_id": "Q-CON-01", "response": 5},
      {"question_id": "Q-CON-02", "response": 2},
      ...
    ]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from statistics import mean, stdev
from typing import Any


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def load_json(path: str | Path) -> Any:
    with open(path) as f:
        return json.load(f)


def softmax(logits: dict[str, float]) -> dict[str, float]:
    """Numerically stable softmax over a dict of {label: logit}."""
    if not logits:
        return {}
    m = max(logits.values())
    exps = {k: math.exp(v - m) for k, v in logits.items()}
    s = sum(exps.values())
    return {k: v / s for k, v in exps.items()}


def archetype_distribution(
    trait_vector: dict[str, float],
    archetypes: dict[str, dict[str, Any]],
    traits: list[str],
    temperature: float = 1.0,
) -> dict[str, float]:
    """Map a trait vector to archetype probabilities via cosine similarity + softmax.

    Cosine similarity is direction-only and magnitude-invariant, which gives us
    two important properties:

      1. Calibration: a random respondent (whose trait vector is near origin)
         produces a uniform-ish distribution over archetypes. Distance-based
         scoring fails this check because archetypes closer to origin absorb
         all the random mass.

      2. Robustness to response intensity: a user who picks 7s instead of 5s
         has a higher-magnitude trait vector, but the same direction. Cosine
         scoring sees them as the same personality, which is what we want.

    The 'temperature' parameter sharpens (T<1) or softens (T>1) the resulting
    distribution. T=1 is the default; T≈0.5 produces sharper archetypes if
    you want more confident picks.
    """
    # Vector magnitudes
    def mag(v: dict[str, float]) -> float:
        return math.sqrt(sum(v[t] ** 2 for t in traits)) or 1e-9

    t_mag = mag(trait_vector)

    logits: dict[str, float] = {}
    for name, arch in archetypes.items():
        sig = arch["trait_signature"]
        dot = sum(trait_vector[t] * sig[t] for t in traits)
        cos_sim = dot / (t_mag * mag(sig))
        logits[name] = cos_sim / temperature
    return softmax(logits)


def primary_secondary(distribution: dict[str, float]) -> tuple[str, str]:
    sorted_by_prob = sorted(distribution.items(), key=lambda kv: kv[1], reverse=True)
    if not sorted_by_prob:
        return ("", "")
    primary = sorted_by_prob[0][0]
    secondary = sorted_by_prob[1][0] if len(sorted_by_prob) > 1 else ""
    return primary, secondary


# ---------------------------------------------------------------------------
# Tier 1 — weighted sum + per-user z-score
# ---------------------------------------------------------------------------

def score_tier_1(
    responses: list[dict[str, Any]],
    bank: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    items_by_id = {item["id"]: item for item in bank["items"]}
    traits: list[str] = config["traits"]
    secondary_w: float = config.get("cross_loading_secondary_weight", 0.5)

    raw = [r["response"] for r in responses]
    if not raw:
        raise ValueError("no responses provided")

    user_mean = mean(raw)
    user_sd = stdev(raw) if len(raw) > 1 and stdev(raw) > 0 else 1.0

    # Per-trait list of weighted z-scored contributions
    trait_contribs: dict[str, list[float]] = {t: [] for t in traits}

    for r in responses:
        item = items_by_id.get(r["question_id"])
        if item is None:
            continue
        z = (r["response"] - user_mean) / user_sd
        adjusted = item["polarity"] * z
        if item["primary_trait"] in trait_contribs:
            trait_contribs[item["primary_trait"]].append(adjusted)
        if item.get("secondary_trait") and item["secondary_trait"] in trait_contribs:
            trait_contribs[item["secondary_trait"]].append(adjusted * secondary_w)

    trait_vector = {
        t: (sum(vals) / len(vals)) if vals else 0.0
        for t, vals in trait_contribs.items()
    }

    arch_dist = archetype_distribution(trait_vector, config["archetypes"], traits)
    primary, secondary = primary_secondary(arch_dist)

    return {
        "tier": 1,
        "trait_vector": trait_vector,
        "trait_uncertainty": None,
        "ers_estimate": None,  # implicit in user-z; no separate scalar
        "archetype_distribution": arch_dist,
        "primary_archetype": primary,
        "secondary_archetype": secondary,
        "n_items_answered": len(responses),
    }


# ---------------------------------------------------------------------------
# Tier 2 — Bayesian inference with ERS latent variable
# ---------------------------------------------------------------------------

def score_tier_2(
    responses: list[dict[str, Any]],
    bank: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    """Closed-form Bayesian update with Normal priors and Normal likelihoods.

    Model (per item i):
        expected_response_i = midpoint
                            + polarity_i × T_{primary_i} × discrimination_i
                            + secondary_w × polarity_i × T_{secondary_i} × discrimination_i
                            + ers_factor_i × (raw_response_i - midpoint)

    Priors: T_k ~ Normal(0, 1), ERS ~ Normal(0, 1).

    For each item, we treat the observed response as a noisy linear measurement of
    the relevant traits and run a one-dimensional Kalman update per-trait.
    """
    items_by_id = {item["id"]: item for item in bank["items"]}
    traits: list[str] = config["traits"]
    secondary_w: float = config.get("cross_loading_secondary_weight", 0.5)
    midpoint: float = float(config["scale"]["midpoint"])
    discrimination: float = 1.0  # uniform unless learned from pilot data
    obs_sd: float = 1.5  # how noisy each Likert response is, in scale units

    # 1. ERS calibration from first N responses (default 5)
    n_calib = config.get("ers", {}).get("calibration_first_n_items", 5)
    calib = responses[:n_calib]
    if calib:
        avg_dev = mean(abs(r["response"] - midpoint) for r in calib)
    else:
        avg_dev = 0.0
    # Population baseline: a flat Likert deviates ~1.5 from midpoint on average
    population_avg_dev = 1.5
    ers_estimate = (avg_dev - population_avg_dev) / population_avg_dev  # normalized z-ish

    # 2. Posterior: Normal(mean, var) per trait. Start at prior.
    trait_mean: dict[str, float] = {t: 0.0 for t in traits}
    trait_var: dict[str, float] = {t: 1.0 for t in traits}

    for r in responses:
        item = items_by_id.get(r["question_id"])
        if item is None:
            continue

        # Effective response after ERS normalization
        deviation = r["response"] - midpoint
        normalized_dev = deviation / max(1.0 + ers_estimate, 0.5)  # divide by user's response gain
        observed = midpoint + normalized_dev

        # Linear measurement: observed = midpoint + polarity * trait * discrimination + noise
        # Solve for trait contribution: trait * discrimination = (observed - midpoint) / polarity
        # Then update primary trait posterior with Kalman-style update
        meas = (observed - midpoint) / item["polarity"]  # signed measurement of trait * discrimination

        for trait_role, weight in [("primary_trait", 1.0), ("secondary_trait", secondary_w)]:
            t_key = item.get(trait_role)
            if not t_key or t_key not in traits:
                continue
            effective_disc = discrimination * weight
            if effective_disc == 0:
                continue
            # Likelihood mean: trait * effective_disc ; observation: meas
            # Equivalent measurement of trait alone: meas / effective_disc
            meas_of_trait = meas / effective_disc
            meas_var_of_trait = (obs_sd ** 2) / (effective_disc ** 2)

            prior_mean = trait_mean[t_key]
            prior_var = trait_var[t_key]
            # Kalman update
            post_var = 1.0 / (1.0 / prior_var + 1.0 / meas_var_of_trait)
            post_mean = post_var * (prior_mean / prior_var + meas_of_trait / meas_var_of_trait)

            trait_mean[t_key] = post_mean
            trait_var[t_key] = post_var

    arch_dist = archetype_distribution(trait_mean, config["archetypes"], traits)
    primary, secondary = primary_secondary(arch_dist)

    return {
        "tier": 2,
        "trait_vector": trait_mean,
        "trait_uncertainty": trait_var,
        "ers_estimate": ers_estimate,
        "archetype_distribution": arch_dist,
        "primary_archetype": primary,
        "secondary_archetype": secondary,
        "n_items_answered": len(responses),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--question-bank", required=True, help="Path to question_bank.json")
    parser.add_argument("--scoring-config", required=True, help="Path to scoring.json")
    parser.add_argument("--responses", required=True, help="Path to responses.json")
    parser.add_argument("--tier", type=int, choices=[1, 2], default=1, help="Scoring tier (default: 1)")
    parser.add_argument("--output", help="Optional path to write result JSON")
    args = parser.parse_args()

    bank = load_json(args.question_bank)
    config = load_json(args.scoring_config)
    responses = load_json(args.responses)

    if args.tier == 1:
        result = score_tier_1(responses, bank, config)
    else:
        result = score_tier_2(responses, bank, config)

    out = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(out)
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

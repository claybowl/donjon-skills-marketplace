# Scoring Approaches — From Weighted Sum to Bayesian Adaptive

Read this when implementing scoring or choosing between scoring tiers. Three tiers in order of complexity. Pick the simplest tier that serves the decision the test feeds.

---

## Tier 1 — Weighted Sum (Likert mean, polarity-handled)

The simplest viable approach. Right answer for MVPs and most internal tools.

### The math

For each trait T:

```
trait_score(T) = (1/N_T) × Σ_{i ∈ items_T} (polarity_i × response_i)
```

Where:
- `items_T` = items with primary_trait == T
- `polarity_i` = +1 (direct) or −1 (reverse-scored)
- `response_i` = the user's answer on the Likert scale

For reverse-scored items on a 1–7 scale, the standard trick is to subtract from 8: `effective_response = 8 − raw_response`. Algebraically equivalent to multiplying by −1 and adding the scale-max-plus-1 constant; pick the form your team finds clearest.

### Cross-loading items

If an item has both `primary_trait` and `secondary_trait`, give the secondary 50% weight (or whatever your design.md specifies):

```
contribution_to_primary = 1.0 × polarity × response
contribution_to_secondary = 0.5 × polarity × response
```

### Poor-person's ERS correction (recommended even at Tier 1)

Z-score each user's responses against their own mean and stddev *before* computing trait scores:

```
user_mean = mean(all_responses_by_user)
user_sd = stddev(all_responses_by_user)
adjusted_response_i = (response_i - user_mean) / user_sd
```

Now an extreme responder who picks 7 with a personal mean of 6 looks like a +1.0 — same as a moderate responder who picks 5 with a personal mean of 4. Removes most response-style noise without requiring the full Bayesian latent-variable treatment.

### Mapping to archetypes

Each archetype is defined by a **trait signature** — a vector of expected trait scores ("the Architect" = high Conscientiousness, high Analytical Thinking, low Sensation Seeking). Map a user's trait vector to archetype probabilities via **cosine similarity + softmax**:

```
archetype_logit_a = cos_sim(trait_vector, signature_a)
archetype_probs = softmax(archetype_logits / temperature)
```

**Why cosine, not squared distance?** Two reasons:

1. **Calibration.** Random respondents land near the trait-vector origin. Distance-based scoring (negative squared distance) makes whichever archetype is closest to origin absorb all the random mass. Cosine similarity is direction-only, so random input produces near-uniform archetype distributions.

2. **Magnitude invariance.** A user who picks 7s instead of 5s has a higher-magnitude trait vector but the same direction. Cosine treats them as the same personality, which is what we want — the magnitude is mostly response style, not personality.

**Mean-center your archetype signatures.** For each trait, the average signature value across all archetypes should be ~0. If the centroid of your archetype signatures sits at, say, (+0.6, +0.7, ...), then the random-respondent's near-zero trait vector is closer to *all* archetypes from one specific angle, biasing the distribution. Centering removes this. The reference template in `assets/scoring_config_template.json` was mean-centered after initial design — you should do the same.

### Pros/cons

**Pros:** Trivial to implement. Easy to debug. Auditable to non-engineers. Stable across small samples.

**Cons:** No learning — weight matrix is hand-authored. No proper uncertainty quantification. ERS correction is approximate.

### When to upgrade

Move to Tier 2 when:
- You have >1k respondents (so Bayesian estimates have enough data to be useful)
- Stakeholders are asking about confidence intervals
- You see ERS-driven failure modes in retest data

---

## Tier 2 — Bayesian Trait Inference with ERS Conditioning

The right answer for most production tests at moderate scale. SoulTrace's approach for the trait inference step.

### Latent variables

Model these per user:

- `T_k ~ Normal(0, 1)` for each trait k (8 traits → 8 latent variables)
- `ERS ~ Normal(0, 1)` — extreme response style

### Likelihood for a response

For item i with primary trait k_i, polarity p_i, and observed response r_i (on a 1–7 Likert):

```
expected_response_i = midpoint + p_i × T_{k_i} × discrimination_i + ERS_factor
P(r_i | T_{k_i}, ERS) = Normal(expected_response_i, sigma_i²)
```

Where:
- `midpoint` = 4 for a 1–7 scale
- `discrimination_i` = the slope; how strongly this item depends on the trait. Learned from training data; 1.0 is fine for items without learned discrimination.
- `ERS_factor` accounts for tendency to use scale extremes; multiplicative on the deviation from midpoint

### Posterior update

After all responses, the posterior over traits is:

```
P(T_1..T_K, ERS | r_1..r_N) ∝ P(T_1..T_K, ERS) × Π_i P(r_i | T_{k_i}, ERS)
```

This is conjugate-friendly if you assume Normal priors and Normal likelihoods, so closed-form posterior updates are possible. In practice, MCMC or variational inference is fine for offline scoring.

For real-time scoring (each response updates posteriors immediately), Kalman-filter-style updates work well — each response is treated as a measurement that contracts the posterior variance.

### ERS calibration

Calibrate ERS from the user's first ~5 responses by fitting their average distance from midpoint:

```
ERS_estimate = mean(|response_i - midpoint|) - population_mean(|response - midpoint|)
```

Then condition all subsequent trait updates on this ERS estimate. The reference scorer at `scripts/score_test.py` implements this.

### Mapping to archetypes

Same weight matrix idea as Tier 1, but now you have full posteriors over traits, so you can propagate uncertainty:

```
For each MCMC sample (or batch of samples):
    sample_archetype_logits = W × sample_trait_vector
    sample_archetype_probs = softmax(sample_archetype_logits)
Average across samples for final archetype distribution.
```

This gives you not just an archetype label but a distribution with calibrated uncertainty. Extremely valuable for agent mimicry — the agent can know how confident it is about each personality dimension.

### Learning the weight matrix

The W matrix that maps traits to archetypes can be hand-authored or learned. To learn it:

1. Collect labeled training data — users who self-identify with archetypes (or whom human raters label).
2. Train a softmax classifier from trait vectors → archetype labels.
3. The classifier weights *are* W.

You can also learn item discriminations and difficulties from the same data using IRT (Item Response Theory). This is the standard approach for adaptive tests.

### Pros/cons

**Pros:** Principled uncertainty. ERS handled correctly. Stable across response styles. Defensible to a stats-savvy stakeholder.

**Cons:** More engineering. Requires labeled data (or hand-authored priors). Less obvious to non-statisticians.

---

## Tier 3 — Adaptive (Information-Gain Question Selection)

The full SoulTrace experience. Right answer for tests at significant scale where saving the user's time matters.

### How adaptive selection works

1. After each response, update the Bayesian posterior (as in Tier 2).
2. Compute entropy per trait: `H(T_k) = -∫ P(T_k) log P(T_k) dT_k`
3. For each candidate next question q:
   - Simulate the response distribution given current posteriors
   - For each possible response r, compute the posterior entropy after observing (q, r)
   - Take the expected posterior entropy over r
   - `IG(q) = current_entropy - expected_posterior_entropy`
4. Add a coverage bonus to ensure all traits get sampled:
   - `IG_adjusted(q) = IG(q) + λ × coverage_bonus(q)`
   - `coverage_bonus(q) = 1 / (1 + sum_of_responses_so_far_for_q's_trait)`
5. Pick `argmax_q IG_adjusted(q)`.

### Stopping rule

Stop when total entropy (sum of per-trait entropies) drops below a threshold. Empirically: ~24 questions for most users, with adaptive routing handling the long tail.

You can also use a fixed cap (e.g., 30 questions) as an upper bound, with adaptive stopping below.

### Pre-computing IG lookup tables

Closed-form IG is intractable for most likelihood/prior combinations, so use Monte Carlo:

1. Sample S=1000 trait vectors from current posterior
2. For each sample, compute expected response to candidate question
3. Histogram the responses → predictive distribution
4. Compute entropy from the histogram

For production, pre-compute a lookup table: for each (question, posterior_state) pair, store the IG. Update incrementally as posteriors shift.

### Pros/cons

**Pros:** Fewest questions (~24 average vs. 50+ for fixed). Stops when results are stable. Best UX.

**Cons:** Significant engineering. Requires good item bank (each question needs accurate discrimination/difficulty estimates). Harder to debug — "why did you ask this question?" requires running the IG computation backward.

### When to use Tier 3

- You have >10k respondents (enough to learn IRT parameters reliably)
- Time-on-task matters (consumer products, mobile)
- You're shipping the SoulTrace-grade experience

For K8 v1, Tier 1 with poor-person's ERS is the right starting point. Plan to upgrade to Tier 2 once you have >1k users.

---

## Reference scorer

`scripts/score_test.py` implements Tiers 1 and 2 (with ERS conditioning). It consumes:

- `question_bank.json` (the items)
- `scoring.json` (weight matrix, archetype definitions)
- `responses.json` (one user's responses)

Returns a result object with:

- Trait vector (8 dimensions)
- Trait posterior variances (Tier 2 only)
- Archetype distribution
- Top archetype label
- ERS estimate

Port to TypeScript / Deno for the K8 edge function. The reference Python is annotated for readability, not performance.

---

## Anti-patterns

1. **Adding scoring rules to one-off questions.** Don't have items where "if user picks 7 on Q23 they're automatically Type Blue." Scoring rules must be uniform across the bank.

2. **Tuning weights to match self-report.** If users self-identify as "Type Blue" and you tune the model to match, you're measuring self-concept, not personality. Tune against external behavioral criteria instead.

3. **Skipping the calibration check.** A scorer that produces non-uniform distributions on random input is biased; ship it and you ship the bias to every user.

4. **Hiding the math.** A user (or an engineer) should be able to ask "why did I get this archetype?" and get a clean answer in terms of trait scores and item contributions. If you can't produce that explanation, the scoring is too opaque.

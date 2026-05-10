# Validation — How to Prove Your Test Actually Works

Read this when preparing to launch a test or when a stakeholder asks "but is it accurate?". Validation is testable in code; this document tells you what to test and how.

## The three checks every test must pass

### 1. Calibration check (testable in code, do this first)

**Hypothesis:** Random respondents should produce a uniform distribution over archetypes.

**Why it matters:** A scorer that's biased toward one archetype will push every user toward that archetype, regardless of their actual personality. The bias gets baked into every result.

**How to run:**

1. Generate 10,000 simulated respondents.
2. For each, sample responses uniformly at random from the Likert range.
3. Run the scorer on each.
4. Histogram the resulting archetypes.

**Pass criterion:** No archetype should appear more than `1.5 × uniform_expected_frequency` or less than `0.5 × uniform_expected_frequency`. For 25 archetypes, uniform is 4% — so no archetype should dominate above ~6% or be starved below ~2%.

**If the test fails:** the scoring is biased. Common causes (in order of frequency):
- **Archetype signatures aren't mean-centered.** If signatures all lean positive in some traits, the centroid drifts off-origin and random respondents cluster around it. Fix: subtract the per-trait mean across all archetypes from each signature.
- **Distance-based scoring with unequal-magnitude signatures.** Switch to cosine similarity (see `references/scoring.md`).
- **Polarity errors** — reverse-scored items not being flipped correctly. Check the `polarity` field on every item.
- **Asymmetric question coverage** — one trait has 3× more items than another, so it dominates the trait vector. Audit items-per-trait counts.

`scripts/calibration_check.py` runs this automatically against any scorer + question bank.

### 2. Retest reliability protocol

**Hypothesis:** The same user, taking the test twice within a few weeks, should get nearly the same result.

**Why it matters:** If retest disagrees, the test is measuring noise, not personality. MBTI fails this badly (~50% flip rate); Big Five passes it well (r > 0.80 on trait scores typically).

**How to run:**

1. Recruit 50+ respondents (more is better).
2. Have them complete the test once.
3. Wait 2–4 weeks (long enough that they don't remember answers; short enough that personality genuinely shouldn't have changed).
4. Have them retake the test.
5. Compute:
   - **Primary archetype agreement rate** — same archetype both times?
   - **Trait correlations** — Pearson r between time-1 and time-2 trait scores
   - **Result distribution overlap** — how similar are the full archetype distributions?

**Pass criteria:**
- Primary archetype agreement: ≥85% (anything below is an MBTI-class failure)
- Trait correlations: r ≥ 0.70 per trait
- Distribution overlap (cosine similarity between time-1 and time-2 archetype probability vectors): ≥0.85

**If the test fails:** items are noisy. Audit each trait's items for low item-total correlations (see `question-construction.md`) and replace the worst.

### 3. Construct validity criterion

**Hypothesis:** The test scores correlate with an external behavioral criterion.

**Why it matters:** A test can be reliable (high retest) and still measure the wrong thing. Construct validity is what makes the test *useful*.

For a personality test feeding an AI agent (K8's case), the natural criterion is:

> **Agents built on this test's output should be recognizable as the user by close friends ≥70% of the time in blinded transcripts.**

That's the operational test of "does the test capture enough to mimic the user." Run it with a small panel:

1. Have user U take the test; build an agent A_U from the results.
2. Run agent A_U through 3–5 typical scenarios (negotiation, casual chat, decision-making).
3. Show the transcripts to U's close friends *blinded* — they don't know which transcripts are A_U vs. someone else.
4. Friends classify each transcript as "this is U" or "this isn't U."
5. Pass criterion: ≥70% recognition.

Other valid criteria depending on use case:
- **Hiring assessments:** trait scores correlate with job performance ratings
- **Matchmaking:** trait scores predict relationship satisfaction at 6 months
- **Self-discovery products:** trait scores correlate with Big Five (or whichever validated reference instrument you're claiming to map to)

**If the test fails:** the trait model isn't capturing the right dimensions for the criterion. Either change the trait model or change the criterion (and update marketing claims accordingly).

---

## Optional but recommended checks

### 4. Internal consistency (Cronbach's alpha)

For each trait's item subset, compute Cronbach's alpha:

```
α = (k / (k-1)) × (1 - Σ var(item_i) / var(sum_of_items))
```

Where k = number of items for the trait.

**Pass criterion:** α ≥ 0.70 per trait. (α > 0.95 is *too* high — your items are redundant; cut some.)

### 5. Item-total correlation

For each item, correlate the item score with the sum of the *other* items measuring the same trait. Items with item-total correlation < 0.30 don't contribute to the trait estimate; cut them.

### 6. Convergent validity vs. a reference instrument

If your test claims to measure Big Five traits, give a sample of users your test *and* the BFI-44, then correlate:

- Your "Conscientiousness" with BFI Conscientiousness → expect r ≥ 0.65
- Same for each trait

If correlations are < 0.5, your trait isn't actually measuring what you're claiming.

### 7. Discriminant validity

Trait scores should *not* correlate too strongly *across* different traits (otherwise you're measuring one underlying factor, not multiple).

- Cross-trait correlations: |r| ≤ 0.4 typically (some pairs naturally correlate, e.g., Openness and Need for Cognition)

If two of your traits correlate at r > 0.7, they're the same trait. Merge them.

### 8. Adversarial / faking-good check

Run a sample of respondents through the test under three conditions:

- Normal answering
- "Fake good" instructions ("answer to make yourself look as desirable as possible")
- "Fake bad" instructions

A robust test shouldn't be *too* fakeable. If "fake good" produces dramatically different archetypes than normal, the test is sensitive to social desirability and needs reverse-scored items rewritten or indirect phrasing added.

---

## Validation plan template (paste into design.md)

```markdown
## Validation Plan

### Pre-launch (must complete)
- [ ] Calibration check: 10k random respondents → uniform archetype distribution within ±50% of expected
- [ ] Pilot bank review: every item has item-total correlation ≥ 0.30
- [ ] Internal consistency: Cronbach's α ≥ 0.70 per trait

### Launch + 4 weeks
- [ ] Retest reliability: 50+ users retested, primary archetype agreement ≥ 85%
- [ ] Trait correlations across retest: r ≥ 0.70 per trait

### Launch + 8 weeks
- [ ] Construct validity (criterion: [insert criterion]): pass criterion met
- [ ] Convergent validity vs. [reference instrument]: cross-correlations ≥ 0.65

### Ongoing
- [ ] Monthly calibration check on production scorer
- [ ] Quarterly retest audit (sample of 50 users from last quarter)
- [ ] Trait drift monitoring: if a trait's distribution shifts >10% month-over-month, investigate
```

---

## What "good enough" looks like in practice

For a v1 product launch, aim for:

- Calibration check passed
- Cronbach's α ≥ 0.65 per trait (slightly relaxed from 0.70)
- Item-total correlations ≥ 0.30 for all production items
- Retest plan in place but not yet executed

For a research-grade or hiring-grade test, raise the bar:

- All checks above
- Retest agreement ≥ 90%
- Convergent validity vs. a published instrument
- Adversarial / faking check
- Cross-cultural pilot if international

---

## Scripts

- `scripts/calibration_check.py` — runs the random-respondent simulation, plots histogram
- `scripts/retest_analysis.py` — (optional, write per project) — takes paired time-1/time-2 data, computes agreement and trait correlations
- `scripts/item_audit.py` — (optional, write per project) — computes item-total correlations and Cronbach's alpha from response data

The calibration check is the only one we ship by default in this skill — it's universally applicable. The other two are project-specific because they depend on the data shape you collect.

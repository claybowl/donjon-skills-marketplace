# Personality Test Methodology — Theory and First Principles

This is the *why* behind everything in `SKILL.md`. Read it when:

- You need to defend a design choice to a stakeholder
- A user is asking "but is this really accurate?"
- You're tempted to invent traits, skip validation, or use forced binary output
- You want the deeper version of an argument the SKILL.md only hints at

The bulk of this document synthesizes SoulTrace's published methodology because their work is the clearest open articulation of what a modern, psychometrically-sound, AI-friendly personality test looks like. SoulTrace's stack: Bayesian active learning, latent trait inference, ERS conditioning, adaptive question selection. Their team came out of Meta, Google, and Hugging Face — credible enough that we treat their architecture as the reference.

---

## 1. The Two-Stage Architecture (the most important idea in this doc)

```
Answer → Trait Updates (Bayesian) → Weight Matrix × Traits → Softmax → Colors / Archetypes
```

Older systems (and most cheap personality tests) update **archetype probabilities directly** from answers. Question 14 nudges you 8% toward "the Architect," question 15 nudges you 4% toward "the Strategist," and so on. The problem: there's no first-principles reason any specific question should map to any specific archetype. The mapping is a black box, the weights are vibes, and you can't explain to a user why their answer produced their result.

SoulTrace v3.0's breakthrough: **decouple traits from archetypes.**

1. Each answer updates posteriors over **~8 latent traits** (Big-Five-style, peer-reviewed).
2. A **learned weight matrix W (8×K)** transforms the trait vector into K archetype logits.
3. **Softmax** over those logits produces archetype probabilities.

Why this matters:

- **Defensibility.** "This question maps to Conscientiousness, which is one of the Big Five traits validated since 1992 by Costa & McCrae" is a stronger answer than "the table says so."
- **Composability.** The trait vector is the right abstraction for an *AI agent* to consume. Archetypes are for users. Same data, two renderings.
- **Robustness.** If you discover a trait is poorly measured, you fix that one trait — you don't have to retune the whole archetype space.

For Donjon / K8 specifically: **always store the trait vector alongside the archetype.** The agent should consume the trait vector. The user sees the archetype.

---

## 2. The 8 SoulTrace Traits (and why these specifically)

SoulTrace expanded beyond the Big Five to capture dimensions that matter for AI mimicry but Big Five misses or under-weights. None are invented; all are rooted in published personality literature.

| Trait | What it captures | Source |
|---|---|---|
| **Conscientiousness** | Organization, dependability, self-discipline | Costa & McCrae (Big Five) |
| **Need for Cognition** | Enjoyment of effortful thinking | Cacioppo & Petty 1982 |
| **Analytical Thinking** | Preference for systematic vs. intuitive reasoning | Decision-making lit |
| **Agency Motivation** | Drive for achievement, power, influence | McClelland; motivation lit |
| **Promotion Focus** | Orientation toward gains/aspirations vs. losses/duties | Higgins (Regulatory Focus) |
| **Sensation Seeking** | Pull toward novel, intense experiences | Zuckerman 1994 |
| **Emotional Expressivity** | Comfort with displaying emotion | Affective science |
| **Communion Motivation** | Drive for connection and belonging | Bakan; social motivation lit |

Notable choices:

- They **dropped explicit Neuroticism / Emotional Stability** as a single trait and split it functionally — Promotion Focus carries some of it, Emotional Expressivity carries some, the rest is captured by ERS conditioning (see §4).
- They **added decision-style traits** (Analytical Thinking, Need for Cognition) because those matter enormously for agent mimicry — an agent that reasons like the user feels like the user.

You don't have to use exactly these 8. But if you depart, write down which traits you're using and the citation for each.

---

## 3. The 5-Color Layer (and why colors at all)

The 5 colors in SoulTrace (Blue, Green, Yellow, Red, Black) are **archetype labels**, not traits. They emerge from the weight matrix:

- **Blue** ≈ high Conscientiousness, Analytical Thinking, Communion → "the steady, thoughtful one"
- **Green** ≈ balanced across traits → "the adaptive one"
- **Yellow** ≈ high Sensation Seeking, Promotion Focus, Emotional Expressivity → "the energetic one"
- **Red** ≈ high Agency Motivation, intensity, drive → "the powerful one"
- **Black** ≈ high Analytical Thinking, low Communion → "the independent intellectual"

The 25 archetypes are the **5×5 grid** of primary × secondary color. This gives users a memorable label *and* a nuanced position.

Why colors instead of, say, animals or tarot cards? Colors are:

- **Culturally low-baggage** (relative to e.g., zodiac signs, animals)
- **Positional** (you can mix them; you have a *primary* and *secondary*)
- **Already psychologically loaded** in user expectations (red = energy, blue = calm) so the labels feel intuitive

You can pick a different rendering layer (animals, elements, custom names) — but the math underneath should look the same. Continuous trait posteriors → weight matrix → archetype distribution.

---

## 4. ERS — the response-style problem and why everyone ignores it

**The problem:** Some users hit "7" on every question they agree with. Others hit "5" on the same questions. Their underlying personality may be identical; their response style differs.

If you ignore this — and most personality tests do — you measure response style and call it personality. The user who always picks 7 looks more extreme on every trait than the user who picks 5. Their archetypes diverge for reasons that have nothing to do with who they are.

**The fix (per SoulTrace v3.0):**

1. Treat **Extreme Response Style (ERS)** as its own latent variable.
2. Calibrate it from the user's first ~5 answers (their average distance from the scale midpoint).
3. Condition every trait update on the ERS estimate.

In Bayesian form:

```
P(trait | response, ERS) ∝ P(response | trait, ERS) × P(trait)
```

Practically, a user with high ERS who picks "7" is treated as picking ~"5.5" once their style is normalized.

**You should always do this.** Even in Tier 1 weighted-sum scoring, you can z-score each user's responses against their own mean and stddev before summing. That's a poor person's ERS correction, and it's better than nothing.

> "Extreme responders (people who always pick 7) walked away with different results than moderate responders (people who pick 5) even when their underlying personality was identical." — SoulTrace v3.0 blog

---

## 5. Adaptive Question Selection (information gain)

A fixed-battery test asks the same N questions in the same order to everyone. After question 5, the test already knows you're highly conscientious — but it asks questions 6, 7, 8 about conscientiousness anyway, while leaving Sensation Seeking under-sampled.

SoulTrace's adaptive approach:

1. After each response, update the posterior over all traits.
2. Compute entropy (uncertainty) per trait.
3. Pick the next question that maximizes **expected information gain** over high-entropy traits, with a small coverage bonus to ensure all traits get sampled.

```
IG(q) = H(traits_before_q) - E[H(traits_after_q | response)]
IG_adjusted = IG(q) + λ × coverage_bonus(q)
```

Closed-form IG is intractable; in practice you Monte-Carlo-sample from the current posterior, simulate each candidate response, and average the resulting entropy. Pre-computing per-question IG lookup tables is a common optimization.

**The result:** ~24 questions to converge to a stable archetype, vs. 50+ for fixed batteries. Same accuracy or better.

> "Question selection now targets trait uncertainty rather than color uncertainty. We pick the question that maximizes information gain across whichever traits are still wobbly." — SoulTrace v3.0

When to use adaptive vs. fixed:

- **Fixed (Tier 1 scoring)** — MVPs, internal tools, tests with <500 users. Engineering-cheap, easy to reason about.
- **Adaptive (Tier 3 scoring)** — production tests at scale, where saving questions matters and you have labeled training data to compute IG lookup tables.

Tier 2 (Bayesian inference, fixed question order) is the common middle ground.

---

## 6. What "Accurate" Actually Means

Personality tests claim accuracy; few define it operationally. SoulTrace's working definition:

1. **Retest reliability.** Same person, two weeks apart, same primary archetype ≥85% of the time. MBTI fails this badly (~50% flip rate). Big Five passes it (typically r ≥ 0.80 across retests).
2. **Construct validity.** Each trait correlates with established measures. If your "Conscientiousness" doesn't correlate with the NEO PI-R Conscientiousness scale, it's not Conscientiousness — call it something else.
3. **Response-style robustness.** ERS conditioning. See §4.
4. **Calibration.** Random/adversarial answers should produce a uniform distribution over archetypes. If they don't, the model is biased toward whichever archetype absorbs noise.

> "Random answers actually produce a uniform distribution now, which wasn't always the case before." — SoulTrace v3.0

Calibration is **testable in code**. Run 10,000 random respondents through the scorer; histogram the archetypes; check flatness. If you can't do this with your scoring approach, the scoring is too opaque.

---

## 7. Short vs. Long Tests — the diminishing-returns curve

The information gain from each additional question follows a sharp diminishing-returns curve. Empirically:

- **Questions 1–10:** each contributes 5–15% reduction in trait uncertainty
- **Questions 10–25:** each contributes 1–5%
- **Questions 25–50:** each contributes <1%, but completion rate drops fast
- **Questions 50+:** the marginal user fatigue introduces *more noise than signal*

Sweet spot: **15–30 questions** for most use cases. SoulTrace's adaptive approach lands at ~24 average.

If a stakeholder wants 100 questions because it "feels more thorough," push back: long tests don't make results more accurate; they make completion rates worse, and worse completion = more user fatigue = noisier responses = *less* accurate results.

The exception: if you're building a *clinical* instrument (DSM-style screening, hiring assessment) where stakes justify length, longer is fine. But for AI mimicry, agent personalization, or product onboarding, stay under 30.

---

## 8. Differentiation vs. Common Frameworks

**vs. MBTI**
- MBTI flips ~50% of users on retest. Hard pass on dichotomies.
- MBTI has no published validation against external behavior.
- MBTI's appeal is the archetype copy, not the science. Borrow the copy style; reject the math.

**vs. 16Personalities**
- Static 60-question battery. No ERS correction. No adaptive selection.
- Repackages MBTI dichotomies behind a Big Five surface. The archetype layer is good; the underlying math is MBTI.

**vs. Big Five (NEO PI-R, IPIP, BFI-44)**
- The validated foundation. Use it as the trait backbone whenever possible.
- Critique: returns five abstract percentile scores, not memorable archetypes. Users find it harder to recognize themselves. Solution: Big Five backbone + archetype layer on top.

**vs. SoulTrace itself**
- Strongest published methodology in the consumer-AI space.
- The only published system that explicitly models ERS as a latent variable.
- Their archetype copy is excellent; study it.

---

## 9. Design Philosophy in Six Principles

These are the principles that should shape every test you produce:

1. **Root in theory, not intuition.** Traits come from peer-reviewed literature. Cite.
2. **Separate signal from noise.** Model response style as a confound, not personality.
3. **Adapt over fixed-force.** Use information gain when scale justifies it; use Bayesian even when you can't.
4. **Validate relentlessly.** Retest, calibrate, simulate, A/B.
5. **Explain the math.** Users (and engineers) should be able to trace any result back to specific items and weights.
6. **Iterate on accuracy, not engagement time.** Time-on-page is vanity; retest reliability is substance.

---

## 10. Reading List

**Primary sources (SoulTrace blog):**
- https://soultrace.app/en/blog/soultrace-3-new-trait-model
- https://soultrace.app/en/blog/how-soultrace-works-technical
- https://soultrace.app/en/blog/five-color-personality-system
- https://soultrace.app/en/blog/soultrace_methodology
- https://soultrace.app/en/blog/accurate-personality-test
- https://soultrace.app/en/blog/personality-test-questions
- https://soultrace.app/en/blog/short-personality-test
- https://soultrace.app/en/blog/real-personality-test
- https://soultrace.app/en/blog/best-personality-test

**Foundational personality psychology:**
- Costa, P. T., & McCrae, R. R. (1992). *Revised NEO Personality Inventory (NEO PI-R)*
- Cacioppo, J. T., & Petty, R. E. (1982). The Need for Cognition. *Journal of Personality and Social Psychology* 42(1).
- Higgins, E. T. (1997). Beyond Pleasure and Pain. *American Psychologist* 52(12).
- Zuckerman, M. (1994). *Behavioral Expressions and Biosocial Bases of Sensation Seeking.*
- Goldberg, L. R. (1992). The development of markers for the Big-Five factor structure.
- John, O. P., Donahue, E. M., & Kentle, R. L. (1991). The Big Five Inventory.

**Bayesian / IRT / adaptive testing literature:**
- Lord, F. M. (1980). *Applications of Item Response Theory to Practical Testing Problems.*
- van der Linden, W. J., & Glas, C. A. W. (Eds., 2010). *Elements of Adaptive Testing.*

# Trait Models — How to Choose

Read this when the user is choosing between trait models or asking which traits their test should measure.

## TL;DR — heuristics for picking

| If the user wants… | Use… |
|---|---|
| Fastest path to "good enough" for an MVP | **Big Five (BFI-10 or BFI-44)** |
| Agent-mimicry (K8's primary use case) | **Big Five backbone + 3 SoulTrace extensions** |
| Maximum scientific defensibility | **HEXACO + Big Five validation set** |
| Recognizable archetypes for marketing/consumer | **Big Five backbone + 5-color archetype layer** |
| Hiring or clinical screening | Stop. This skill isn't for that. Use a validated commercial instrument. |

The default recommendation for Donjon work is the **second row**: Big Five + a few traits that matter for AI agents but Big Five misses.

---

## 1. The Big Five (OCEAN) — the validated foundation

Five trait dimensions, ~50 years of validation, hundreds of cultures sampled. The closest thing personality psychology has to a periodic table.

| Trait | What it captures |
|---|---|
| **Openness** | Curiosity, imagination, aesthetic sensitivity, openness to experience |
| **Conscientiousness** | Organization, dependability, self-discipline, achievement striving |
| **Extraversion** | Sociability, energy, positive affect, assertiveness |
| **Agreeableness** | Warmth, cooperation, trust, altruism |
| **Neuroticism** | Emotional reactivity, anxiety, vulnerability to stress (often inverted to "Emotional Stability") |

**Standard instruments:**
- **BFI-44** (44 items) — research-grade, validated cross-culturally
- **BFI-10** (10 items) — short form for MVPs
- **NEO PI-R** (240 items) — full clinical-grade with 6 facets per trait. Overkill for product use.
- **IPIP** (open source pool) — pull items à la carte

**Use the Big Five when:** you want the cheapest validated foundation. It's the right answer ~70% of the time.

**Limitations:**
- Returns five percentile scores, not archetypes. Users find this less memorable. Layer archetypes on top for consumer use.
- Doesn't capture decision style well (Analytical vs. Intuitive). Add Need for Cognition or Analytical Thinking for AI mimicry.
- Doesn't capture motivation orientation cleanly (achievement-seeking vs. security-seeking). Add Promotion Focus.

---

## 2. SoulTrace's 8 — Big Five plus AI-mimicry seasoning

SoulTrace's expanded model. Conceptually: Big Five with one trait dropped (Neuroticism → handled by ERS + Promotion Focus) and four traits added that matter for behavioral prediction.

| Trait | Big Five mapping | Added value |
|---|---|---|
| **Conscientiousness** | = Big Five C | (none — same trait) |
| **Need for Cognition** | weakly correlates with Openness | Decision style: enjoys effortful thinking |
| **Analytical Thinking** | weakly correlates with Openness | Decision style: systematic vs. intuitive |
| **Agency Motivation** | partially Extraversion | Drive for achievement, power |
| **Promotion Focus** | partially Neuroticism (inverted) | Goal orientation (gains vs. losses) |
| **Sensation Seeking** | partially Extraversion + Openness | Novelty-seeking |
| **Emotional Expressivity** | partially Extraversion | Comfort showing emotion |
| **Communion Motivation** | = Agreeableness flavor | Drive for connection |

**Use the SoulTrace 8 when:** you're building for agent mimicry, AI personalization, or any case where decision style and motivation matter as much as social behavior. **K8's default.**

**Limitations:**
- Some traits cross-load on Big Five dimensions, so you can't directly compare scores to a Big Five reference.
- Less standardized — fewer validated item banks to draw from.

---

## 3. HEXACO — when you want a sixth dimension

Six factors instead of five. Adds **Honesty-Humility** as its own dimension (Big Five buries this inside Agreeableness).

| Trait | Notes |
|---|---|
| **Honesty-Humility** | Sincerity, fairness, modesty (the H-factor) |
| **Emotionality** | Anxiety, sentimentality, dependence |
| **Extraversion** | Like Big Five E |
| **Agreeableness (HEXACO version)** | Forgivingness, gentleness, patience |
| **Conscientiousness** | Like Big Five C |
| **Openness to Experience** | Like Big Five O |

**Use HEXACO when:** the test is for hiring, ethical/integrity assessment, or any context where sincerity and fairness matter as their own signal.

**Limitations:**
- Smaller validation literature than Big Five (still strong, just smaller).
- The H-factor is sensitive to social desirability — users will fake-good on it harder than other traits. Mitigate with reverse-scored items and indirect phrasing.

---

## 4. Custom trait models — when and how

**Default position: don't.** Inventing traits is the #1 way personality tests become astrology.

If the user *insists* on a custom trait, hold them to this bar before adding it:

1. **Define operationally.** Not "Visionary Drive" — write a one-sentence behavioral definition.
2. **Cite supporting literature.** If no peer-reviewed work supports it, it isn't a trait yet.
3. **Demonstrate non-redundancy.** Show how it differs from existing traits. If it's just Conscientiousness in a costume, drop it.
4. **Plan validation.** Construct validity check + retest reliability. If you can't validate it, you're shipping vibes.

If a stakeholder demands a brand-flavored trait for marketing purposes, here's the compromise: **internally measure a validated trait; render the brand-flavored label at the result layer.** "Visionary Drive" can be the user-facing name for what your scorer treats as Promotion Focus + Need for Cognition.

---

## 5. Specialized models worth knowing

These are not your default, but they exist and you may encounter them.

- **MBTI / 16 Personalities** — Reject for math reasons (see methodology.md). Borrow the archetype-copy *style*; throw away the dichotomy.
- **DISC** — Workplace-focused. Four dimensions. Used widely in corporate training. Validity is mixed; use only if the user is in that ecosystem.
- **Enneagram** — Nine types. Origins are esoteric, but the type descriptions are genuinely insightful. Cannot ground statistically; treat as inspiration for archetype copy, not measurement.
- **VIA Character Strengths** — 24 character strengths; positive psychology lineage. Good for self-development apps; less useful for trait inference.
- **Schwartz Values** — 10 cross-cultural value dimensions. Different beast (values, not traits) but useful for goal/motivation modeling. Pair with Big Five rather than replace it.

---

## 6. How to write down your trait model in `design.md`

Always include this table for the model you choose:

```markdown
## Trait Model

| Trait | Operational Definition | Source / Citation | Items |
|---|---|---|---|
| Conscientiousness | Tendency to be organized, dependable, self-disciplined | Costa & McCrae (1992) NEO PI-R | Q-CON-01 .. Q-CON-06 |
| Need for Cognition | Enjoyment of effortful cognitive activity | Cacioppo & Petty (1982) | Q-NFC-01 .. Q-NFC-05 |
| ...
```

Without this table, no one can audit the test. With it, the test is defensible to engineers, designers, and the legal team.

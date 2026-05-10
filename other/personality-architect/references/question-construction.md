# Question Construction — How to Write Items That Actually Measure

Read this when writing items, auditing existing items, or explaining to a user why their draft questions need rework.

## The seven rules

### 1. Behavioral over abstract

Questions should ask about *what people do*, not *what they are*.

- ✗ "I am organized." — abstract self-concept
- ✓ "I keep my workspace tidy." — behavior

Self-concept items get ~30% more variance from social desirability bias. Behavioral items measure the trait; self-concept items measure how respondents *want to see themselves.*

### 2. Specific over vague

- ✗ "I am sometimes impulsive." — meaningless qualifier
- ✓ "I tend to start projects before I've thought them through." — concrete, image-able

Vague items recruit different cognitions in different respondents. Specific items recruit similar cognitions, which means similar respondents answer similarly — which is what you want for a measurement instrument.

### 3. One trait per question primarily

Each item should have a clear primary trait. **Cross-loading on one secondary trait is fine and often desirable** for coverage efficiency, but never have items that load equally on three+ traits — the signal becomes uninterpretable.

```json
{
  "id": "Q-NFC-03",
  "text": "I find satisfaction in puzzling out how things work.",
  "primary_trait": "need_for_cognition",
  "secondary_trait": "openness",
  "polarity": 1
}
```

### 4. Mix polarity (reverse-score half)

For each trait, **roughly half the items should be reverse-scored.**

- Direct: "I follow through on plans I make." (high score = high Conscientiousness)
- Reverse: "I often abandon tasks before finishing them." (high score = LOW Conscientiousness; flip during scoring)

Why: without polarity mixing, users can acquiesce-bias their way to whatever archetype sounds nice. Reverse-scored items break that. They also expose flat-line responders (users picking the same number for everything) — those users will produce inconsistent within-trait scores when polarity is mixed.

### 5. Anchor extremes; consider middle anchors

For Likert scales, **always label the endpoints.** "Strongly Disagree" / "Strongly Agree" are minimum.

For 7-point scales, anchoring 1, 4, 7 is often clearer than just 1 and 7:

| 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|
| Strongly Disagree |  |  | Neutral |  |  | Strongly Agree |

Avoid 5-point scales with a "Neutral" middle for personality items — neutrals invite hiding. If you must use 5-point, monitor each user's response variance; flag flat-liners.

### 6. Avoid double-barrels

Each item should ask about exactly one thing.

- ✗ "I am calm and confident." — two traits at once
- ✓ "I stay calm under pressure." (Emotional Stability) + "I express my opinions confidently." (Extraversion)

Double-barrels force respondents to pick the average of two traits, which is exactly the noise we're trying to avoid.

### 7. Watch for cultural and contextual loading

An item like "I enjoy small talk" measures different things in cultures where small talk is the norm vs. cultures where it's seen as superficial. For tests with international users:

- Pilot items across at least three cultures before fixing the bank
- Avoid culturally specific examples ("I like watching baseball" — not a personality item; a culture item)
- When in doubt, use the more abstract behavioral phrasing

---

## The item-writing workflow

1. **Pick the trait.** Look at coverage across the bank — which traits need more items?
2. **Pick the polarity.** Need a direct or reverse item for this trait?
3. **Brainstorm 3 candidate phrasings.** Aim for behavioral specificity.
4. **Score the candidates against the seven rules.** Pick the strongest.
5. **Write the metadata** (primary trait, secondary trait, polarity, anchors).
6. **Add to bank with status `draft`.** Items get promoted to `pilot` after a colleague review and to `production` after pilot data shows discrimination.

---

## Items that fail the bar (and why)

**Bad:** "I am a deep thinker."
- Abstract self-concept
- Cultural loading (deep thinker is a positive label; everyone wants to be one)
- Untargeted: could load on Openness, Need for Cognition, Analytical Thinking, or none

**Bad:** "I sometimes feel down."
- Trivially true (everyone feels down sometimes)
- No discrimination — almost everyone agrees, so the item provides no information
- "Sometimes" is a hedge that lets respondents agree without commitment

**Bad:** "I prefer thinking alone over collaborating with others."
- Double-barrel: thinking alone vs. collaborating are two things, not opposites
- Forces respondents to pick when both might be true

**Bad:** "I am the kind of person who gets things done."
- Asks about identity, not behavior
- Universally socially desirable — people will agree even if it's false
- Tells you nothing about Conscientiousness specifically

**Good:** "I keep my commitments to others, even when it's inconvenient." (Conscientiousness, direct, behavioral, specific, anchored to a real situation.)

**Good:** "I'd rather work through a problem methodically than rely on a hunch." (Analytical Thinking, direct, captures decision style, contrasts with intuitive thinking.)

**Good:** "I lose interest in tasks once the novelty wears off." (Sensation Seeking + reverse-scored Conscientiousness, behavioral, captures a real and recognizable pattern.)

---

## Special question types

### Forced-choice (ipsative) items

```
Which is more like you?
A) I plan my day in advance.
B) I take my day as it comes.
```

Pros: harder to fake; reduces ERS issue.
Cons: produces ipsative scores (relative, not absolute), which complicates Bayesian inference. Usually mix with Likert items rather than replacing them.

### Scenario items

```
You're at a party where you don't know most people. You usually:
A) Find one person and have a long conversation.
B) Meet as many people as possible.
C) Find a quiet corner with one friend.
D) Leave early.
```

Pros: high engagement; captures behavioral preference vividly.
Cons: harder to score (each option needs trait weights); harder to write well; scenarios date quickly.

Use sparingly — maybe 10–20% of a bank — for engagement boost.

### Voice / open-ended items (relevant for K8)

```
"Tell me about a time you had to make a hard decision."
```

Pros: rich data, hits multiple traits at once, captures linguistic style.
Cons: requires LLM scoring (which is what K8 already does in `analyze-voice-transcript`); inter-rater reliability is harder to establish.

For K8 specifically: voice items work best as a **complement** to a Likert bank, not a replacement. Use Likert for trait inference; use voice transcripts for linguistic-style fingerprinting that the agent can imitate.

---

## Pilot data — when items become real

Items in the bank should pass through three stages:

1. **Draft** — written by an author, not yet reviewed.
2. **Pilot** — reviewed, deployed to a sample (~50–200 respondents). Collect responses.
3. **Production** — promoted after passing the pilot bar:
   - **Item-total correlation** with its primary trait ≥ 0.30
   - **Variance** across respondents — variance < 0.5 means the item doesn't discriminate; cut it
   - **No floor/ceiling effects** — no item should have >80% of respondents picking the same answer

Items that fail get rewritten or cut. Aim to ship a bank where every production item has earned its slot.

---

## How many items per trait?

| Bank length | Items per trait (target) | Use case |
|---|---|---|
| Short (10–15 total) | 2–3 | MVP, screener, sub-scale |
| Standard (20–30) | 4–6 | Default for product use |
| Long (40–60) | 7–10 | Research-grade, clinical |

Below 3 items per trait, the trait estimate is noisy. Above 8 items per trait, you're getting diminishing returns. Default for K8: 4–6 items per trait, ~25 items total.

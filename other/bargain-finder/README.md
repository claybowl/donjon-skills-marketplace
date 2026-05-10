# Bargain Finder

> Find local marketplace bargains via browser tools and send top deals to Telegram

## Quick Start

```
@bargain-finder find deals for desk, chair, and bookshelf
```

## What It Does

This skill automates the hunt for great local deals on:
- **Facebook Marketplace** — Local seller listings
- **Craigslist** — Classified ads

It scans both platforms, applies intelligent filtering, and sends you a curated list of the top 3–5 bargains with explanations of why each is a great deal.

## Setup

### 1. Browser Extension

Ensure Chrome is running with the OpenCode browser extension installed.

### 2. Telegram Configuration

Set up your Telegram bot (see telegram skill for details):
- Bot token
- Chat ID for receiving notifications

### 3. Location

Default search center: **957 Hayes St, San Francisco, CA (94117)**  
Radius: 5 miles

To change location, mention it in your prompt or modify the skill defaults.

## Usage Examples

### Basic Search

```
@bargain-finder search for coffee table, rug, and floor lamp
```

### With Price Cap

```
@bargain-finder find iPhone under $300
```

### Brand Preference

```
@bargain-finder look for Sonos speakers or Bose soundbar
```

### Condition Filter

```
@bargain-finder find like-new or new patio furniture
```

### Multiple Items

```
@bargain-finder search for:
- yamaha receiver
- bookshelf speakers
- turntable
- vinyl records
```

## How It Works

1. **Builds search URLs** for Facebook Marketplace and Craigslist
2. **Applies filters** (distance, price, condition)
3. **Collects listings** from the first page of results
4. **Scores deals** using:
   - Distance (0–1 mile = best)
   - Price vs typical market rate
   - Condition quality (photos, description)
   - Urgency signals ("moving", "must go", "OBO")
5. **Ranks top 3–5** and sends to Telegram

## Deal Scoring

### Distance Rules

| Distance | Priority | Requirement |
|----------|----------|-------------|
| 0–1 mile | ⭐⭐⭐ Always include | Best location |
| 1–3 miles | ⭐⭐ Include if price is good | Competitive pricing |
| 3–5 miles | ⭐ Only if insanely cheap | Must be ~50% below typical price |

### Auto-Excluded Keywords

Listings containing these are skipped:
- `broken`
- `for parts`
- `repair`
- `not working`

## Telegram Output

Example message format:

```
*Daily Bargains (SF 957 Hayes St)* 🛍️

1) $120 — Yamaha receiver + speakers (0.8 mi) [FB link]
   Why it's a deal: ~50% below typical; clean photos, complete set.
   Condition: described as "like new," no damage language.
   Notes: pickup today, seller says "must go."

2) $80 — Solid wood coffee table (2.2 mi) [CL link]
   Why it's a deal: price below similar listings nearby.
   Condition: solid wood, minor scuffs only.
   Notes: moving sale, quick pickup.
```

## Scheduling

Run daily at 9 AM automatically:

```yaml
---
schedule: "0 9 * * *"
---

@bargain-finder
Find top 3–5 deals near 957 Hayes St, San Francisco.
Search Facebook Marketplace and Craigslist for: desk, chair, monitor.
Send results via Telegram.
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Facebook shows login page | Log into Facebook in Chrome first |
| No results found | Try broader search terms or increase radius |
| Telegram not receiving | Check bot token and chat ID configuration |
| Filters reset | Re-apply location and radius after each search |
| Slow performance | Normal — browser automation takes time |

## Tips for Better Results

1. **Be specific** — "ergonomic office chair" beats "chair"
2. **Include brands** — helps filter quality listings
3. **Set price caps** — avoids overpriced results
4. **Check frequently** — good deals go fast
5. **Verify before meeting** — always confirm item condition in person

## Safety Notes

- Meet sellers in public places when possible
- Bring a friend for high-value items
- Trust your instincts — if a deal seems too good to be true, verify carefully
- Never share payment info before seeing the item

---

*Happy deal hunting! 🎯*

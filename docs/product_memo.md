# Product memo: a "Runs small / Runs large" size tag

**To:** Head of Product, Fashion · **Re:** cutting size-related returns · **Data:** 192,274 RentTheRunway reviews (2010–2018)

## Problem

Wrong size is one of the top reasons fashion orders come back. In this data, **26.2%** of reviews (50,428 of 192,274) say the item ran small (13.4%) or large (12.8%). Each misfit is a likely return, a reshipment, and an unhappy customer.

## Evidence

- **Misfits sit on a small set of items.** The 534 items with 20+ misfit reviews are **9.1%** of the catalogue but carry **52.8%** of all misfit reviews (query 07).
- **Those items lean one way.** Of the 1,592 items with 30+ reviews, **282 run small** and **227 run large** (25%+ of reviews in one direction, at least twice the other). On these 509 items (8.7% of all items), **40.4%** of reviews say "too small" (runs-small items) and **41.2%** say "too large" (runs-large items), about three times the site-wide rates. Together that is **16,240 misfit reviews, 32.2% of all misfits**, on 8.7% of items (queries 03, 08).
- **The direction depends on the shopper's size.** Small sizes mostly complain "too large" (size 1: 18.2% large vs 5.4% small); large sizes mostly "too small" (size 28: 20.4% small vs 8.4% large) (query 04). On the top runs-small dress (item 172027), 11.4% of size-1 renters said small, rising to 54.4% at size 16.
- **Most misfits are about cut and labelling, not fabric.** In a Gemini-tagged sample of 491 misfit reviews, 52.7% of "small" reviews were "too tight", 21.6% of tagged misfits said the size label did not match their usual size ("sizing inconsistent"), and only 3.1% blamed fabric.
- **Body type barely matters.** Misfit rates range only from 25.4% (straight & narrow) to 28.5% (apple) (query 05).
- **Misfits hurt ratings.** 71.0% of "fit" reviews give 5 stars, against 45.4% for "small" and 48.9% for "large". 17.2% of "small" reviews give 3 stars or less, against 4.4% of "fit" reviews (query 06).

## Root cause

Fit problems are mostly an **item problem, not a shopper problem**. Specific items are cut smaller or larger than their label, and the gap grows toward the ends of the size range. Shoppers order their usual size because nothing on the product page tells them the item is off. The information is already there in past reviews, but it is buried in free text.

## Proposed feature

1. **Size tag on flagged items:** "Runs small – consider sizing up" (or "Runs large – consider sizing down") near the size picker, for items that meet the rule above. The rule is re-run nightly so new items qualify once they reach 30 reviews.
2. **Size-aware suggestion:** when the shopper picks a size, show what past buyers of *that size* reported, e.g. on item 172027: "44.5% of size-12 renters said this ran small. Consider one size up." This handles the size-dependent direction above.

No model is needed. Both parts are SQL counts on existing review data.

## Success metrics

| Type | Metric | Why |
|---|---|---|
| Primary | Size-related return rate on flagged items | The direct goal |
| Secondary | Add-to-cart → order conversion on flagged items | The tag should not scare buyers away |
| Secondary | Average rating and 5-star share on flagged items | Fewer misfits should lift ratings |
| Guardrails | Overall conversion, returns for non-size reasons, order value | No harm elsewhere |

## A/B test design

- **Unit:** shopper (randomise by user ID, 50/50), so one person always sees the same version.
- **Control:** today's product page. **Treatment:** tag + size-aware suggestion on the 509 flagged items.
- **Analysis population:** orders of flagged items only (other pages are identical in both arms).
- **Sample size:** the baseline misfit rate on flagged items, in the flagged direction, is 40.8% (16,240 of 39,849 reviews). Detecting a 10% relative drop (to 36.7%) at 5% significance and 80% power needs about **2,239 orders of flagged items per arm** (two-proportion test).
- **Duration:** at least two full weeks to cover weekday and weekend shopping, even if the sample is reached sooner.
- **Decision rule:** ship if the size-related return rate falls significantly and conversion does not drop by more than 1 point.

## Risks

- **Fewer orders:** "Runs small" may push some shoppers away. Watch conversion as a guardrail.
- **Stale or noisy flags:** an item with 30 reviews can be flagged by chance, and a re-cut item keeps an old flag. Re-compute nightly and require both thresholds.
- **Reviews ≠ returns:** this analysis uses fit reviews as a stand-in for size returns. The A/B test must measure actual returns.
- **Bias in who reviews:** unhappy customers may review more often, which can inflate misfit rates. This affects all items alike, so the ranking of items is less affected than the levels.

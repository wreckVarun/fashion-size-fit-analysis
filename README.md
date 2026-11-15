# Fashion Size Fit Analysis

Where do fit problems concentrate in online fashion, and what one product feature would cut size-related returns?

SQL analysis of 192,274 RentTheRunway reviews in which each customer said whether the item fit, ran small or ran large.

**Live dashboard:** https://wreckvarun.github.io/fashion-size-fit-analysis/
**Product memo:** [docs/product_memo.md](docs/product_memo.md)

---

## The business problem

In online fashion, the wrong size is one of the top reasons for returns. Every size return costs two shipments, a cleaning or restock, and often a lost customer. If we know *which items* cause fit problems and *in which direction*, the product page can warn shoppers before they order.

## Dataset

- **Source:** [Clothing Fit Dataset for Size Recommendation](https://www.kaggle.com/datasets/rmisra/clothing-fit-dataset-for-size-recommendation) (Misra et al., RecSys 2018), RentTheRunway file. Kaggle requires a login to download, so `scripts/download_data.py` fetches the same file from the authors' public host at UC San Diego.
- **Columns used:** fit (`fit` / `small` / `large`), item, category, size ordered, rating, body type, height, weight, bust size, age, review text.
- **Size:** 30.7 MB gzipped JSON. It is downloaded by the script and not stored in this repo.

| Stage | Rows |
|---|---|
| Raw file | **192,544** |
| Removed: exact duplicate rows | 189 |
| Removed: same user, item, date and review text as another row | 1 |
| Removed: rating missing | 80 |
| **Clean table used for analysis** | **192,274** (5,850 items, 105,508 users, 61 categories) |

Values that were fixed but kept: 378 ages under 18 or over 90 set to missing, and 339 rows whose category was merged with its plural form (e.g. `pant` → `pants`). Height (`5' 8"` → 68 inches), weight (`137lbs` → 137) and bust size (`34d` → band 34, cup `d`) were parsed into numbers, and ratings (2–10) converted to 1–5 stars. The full log is in [`outputs/cleaning_log.csv`](outputs/cleaning_log.csv).

## How to run it

Needs Python 3.9+. One command:

```bash
pip3 install -r requirements.txt && python3 run_all.py
```

| Step | Script | Output |
|---|---|---|
| 1. Download | `scripts/download_data.py` | `data/raw/renttherunway_final_data.json.gz` |
| 2. Clean | `scripts/clean_data.py` | `data/clean_reviews.csv`, `outputs/cleaning_log.csv` |
| 3. Load | `scripts/load_duckdb.py` | `data/fit.duckdb` |
| 4. Run SQL | `scripts/run_queries.py` | one CSV per query in `outputs/` |
| 5. Tag reasons (optional) | `scripts/tag_reasons.py` | `outputs/review_reasons*.csv` |
| 6. Dashboard | `scripts/build_dashboard.py` | `docs/index.html` (published with GitHub Pages) |

**Optional Gemini step.** If `GEMINI_API_KEY` is set (a free key from Google AI Studio), step 5 sends a fixed random sample of 500 misfit reviews to Gemini in batches of 25 and gets back JSON that must match a schema: one reason per review out of *too tight, too long, sizing inconsistent, fabric, other*. Without a key the step prints a message and is skipped. The published results in `outputs/review_reasons*.csv` were produced with `gemini-flash-lite-latest` (the default; set `GEMINI_MODEL` to use another).

```bash
export GEMINI_API_KEY=your-key
python3 scripts/tag_reasons.py
```

## SQL queries

A review is a **misfit** when it says the item ran small or large.

| File | Question it answers |
|---|---|
| [`01_misfit_rate_overall.sql`](sql/01_misfit_rate_overall.sql) | What share of reviews are misfits? |
| [`02_misfit_by_category.sql`](sql/02_misfit_by_category.sql) | Misfit rate by category (500+ reviews) |
| [`03_items_run_small_or_large.sql`](sql/03_items_run_small_or_large.sql) | Which items (30+ reviews) run small or large? |
| [`04_misfit_by_size.sql`](sql/04_misfit_by_size.sql) | Misfit rate and direction by size ordered |
| [`05_misfit_by_body_type.sql`](sql/05_misfit_by_body_type.sql) | Misfit rate by body type |
| [`06_rating_gap.sql`](sql/06_rating_gap.sql) | Rating gap between fit and misfit reviews |
| [`07_repeat_offenders.sql`](sql/07_repeat_offenders.sql) | Do a few items collect most misfits? |
| [`08_feature_reach.sql`](sql/08_feature_reach.sql) | How many misfits happen on flagged items, in the flagged direction? |

**"Runs small" rule (query 03):** the item has 30+ reviews, at least 25% of them say small (about double the site-wide 13.4%), and small reviews outnumber large ones at least 2 to 1. "Runs large" is the mirror image.

## Key findings

**1. About 1 in 4 reviews is a misfit, split evenly between small and large.**
26.2% of reviews (50,428 of 192,274) say the item ran small (13.4%) or large (12.8%). *(01)*

**2. Misfits pile up on a few items, not across the catalogue.**
The 534 items with 20+ misfit reviews are 9.1% of items but hold 52.8% of all misfit reviews. The 151 items with 50+ misfit reviews (2.6% of items) alone hold 30.8%. *(07)*

**3. 509 items clearly run one way, and they carry a third of all misfits.**
Of 1,592 items with 30+ reviews, 282 run small and 227 run large. On runs-small items 40.4% of reviews say "too small", and on runs-large items 41.2% say "too large", about three times the site-wide rates. These 509 items (8.7% of items) account for 16,240 misfit reviews in the flagged direction, 32.2% of all misfits. This is the target for a size tag. *(03, 08)*

**4. Size, not body type, predicts the direction of the problem.**
Small sizes mostly run large (size 1: 18.2% large vs 5.4% small) and large sizes mostly run small (size 28: 20.4% small vs 8.4% large). Body type barely matters: misfit rates range only from 25.4% (straight & narrow) to 28.5% (apple). By category, coats (40.4%, mostly "large") and pants (35.9%) fit worst and gowns best (20.7%), but dresses alone produce 52.1% of all misfits because of their volume. *(02, 04, 05)*

**5. Misfits cost ratings.**
71.0% of "fit" reviews give 5 stars, against 48.9% of "large" and 45.4% of "small" reviews. The average falls from 4.65 to 4.28 (large) and 4.21 (small) stars, and 17.2% of "small" reviews give 3 stars or less vs 4.4% of "fit" reviews. *(06)*

### Why customers say it did not fit (Gemini reason tags)

**Most "too small" complaints are about a tight fit, and 1 in 5 tagged misfits says the size label was off. Fabric is rarely the cause.**
Gemini tagged a random sample of 500 misfit reviews and returned a reason for 491. Overall: too tight 27.9%, sizing inconsistent 21.6%, too long 15.5%, fabric 3.1%, other 32.0%. Among "small" reviews, 52.7% are "too tight"; among "large" reviews, 53.6% are "other", because the reason list has no "too loose" bucket and loose or big complaints were put there. "Sizing inconsistent" (the label did not match the shopper's usual size) is 19.5% of "small" and 23.6% of "large" reviews, which is the gap a size suggestion is meant to close. *(scripts/tag_reasons.py, outputs/review_reasons_summary.csv)*

### Recommendation

Add a "Runs small – consider sizing up" / "Runs large – consider sizing down" tag to the 509 flagged items, plus a size-aware note showing what buyers of the shopper's size reported. Details, metrics and an A/B test design are in the [product memo](docs/product_memo.md).

## Limitations

- **Reviews, not returns.** The data has fit feedback, not return records. A misfit review is used as a stand-in for a size-related return.
- **Rental, not retail.** RentTheRunway customers rent for events, mostly dresses and gowns (71% of reviews). Retail shoppers and other categories may behave differently.
- **Size is a code.** RentTheRunway stores size as a number from 0 to 58, not a labelled US size. Query 04 keeps the 9 main sizes (3,000+ reviews each, 88.1% of reviews); rarer codes such as 5, 9 and 13 have lower misfit rates and may come from a different size scale.
- **Self-reported fit and body type.** Customers choose "small" or "large" and their own body type; both are subjective.
- **Who writes reviews.** Unhappy customers may be more likely to review, which can inflate misfit rates.
- **Thresholds are judgement calls.** 30 reviews, 25% and 2-to-1 were chosen to flag clear cases; other values flag more or fewer items.
- **Old data.** Reviews run from November 2010 to January 2018.
- **Reason tags are machine labels on a sample.** Gemini labelled 491 of 500 sampled reviews, and the sample is only 1.0% of the 50,428 misfit reviews. Spot checks show some wrong labels (e.g. a "too tight" review tagged "too long"), and the five reasons have no "too loose" option, so loose fits land in "other".

## Project structure

```
fashion-size-fit-analysis/
├── run_all.py               # runs everything with one command
├── requirements.txt
├── scripts/
│   ├── download_data.py     # step 1: get the raw reviews
│   ├── clean_data.py        # step 2: clean with pandas, log every removal
│   ├── load_duckdb.py       # step 3: load into DuckDB
│   ├── run_queries.py       # step 4: run sql/*.sql, save CSVs
│   ├── tag_reasons.py       # step 5 (optional): Gemini reason tags
│   └── build_dashboard.py   # step 6: build docs/index.html
├── sql/                     # 8 analysis queries
├── outputs/                 # query results + cleaning log (CSV)
└── docs/
    ├── index.html           # the dashboard (GitHub Pages)
    └── product_memo.md      # one-page PM memo
```

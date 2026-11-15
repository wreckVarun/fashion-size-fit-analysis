"""Optional step: ask Gemini why each misfit review says the item didn't fit.

We take a random sample of 500 misfit reviews (fit = small or large) and ask
Gemini to put each one into one reason bucket. Gemini returns JSON that must
match the schema below, so we never have to parse free text.

Needs a free Gemini API key in the GEMINI_API_KEY environment variable.
Without a key this step prints a message and does nothing.

Outputs:
  outputs/review_reasons.csv          one row per tagged review
  outputs/review_reasons_summary.csv  count and share of each reason
"""
import json
import os
import time

import duckdb
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "data", "fit.duckdb")
OUT_DIR = os.path.join(ROOT, "outputs")
TAGS_PATH = os.path.join(OUT_DIR, "review_reasons.csv")
SUMMARY_PATH = os.path.join(OUT_DIR, "review_reasons_summary.csv")

MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
SAMPLE_SIZE = 500
BATCH_SIZE = 25          # reviews per request: 500 / 25 = 20 requests
PAUSE_SECONDS = 7        # stay under the free tier's requests-per-minute limit
REASONS = ["too tight", "too long", "sizing inconsistent", "fabric", "other"]

# The shape of the answer we want back: a list of {id, reason}.
RESPONSE_SCHEMA = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "id": {"type": "INTEGER"},
            "reason": {"type": "STRING", "enum": REASONS},
        },
        "required": ["id", "reason"],
    },
}

INSTRUCTIONS = """You are reading clothing rental reviews where the customer said the item
did not fit. For each review, pick the ONE main reason it did not fit:
- too tight: tight, snug or small anywhere (bust, hips, waist, shoulders), hard to zip
- too long: too long or too short in length (hem, sleeves, torso)
- sizing inconsistent: the size label did not match their usual size, or sizes differ between parts of the garment
- fabric: no stretch, stiff, thin, see-through, or fabric that fits badly
- other: loose or big in general, or any other reason
Return one entry per review, using the review's id."""


def sample_misfits():
    """Pick the same 500 misfit reviews every time (fixed random seed)."""
    con = duckdb.connect(DB_PATH, read_only=True)
    misfits = con.execute("""
        SELECT review_id, fit, category, review_text
        FROM reviews
        WHERE fit <> 'fit'
    """).df()
    con.close()
    return misfits.sample(SAMPLE_SIZE, random_state=42).reset_index(drop=True)


def tag_batch(client, types, batch):
    """Send one batch of reviews to Gemini and return its list of {id, reason}."""
    lines = []
    for row in batch.itertuples():
        text = str(row.review_text)[:600]  # long reviews are cut to save tokens
        lines.append(f"id {row.review_id} (said it runs {row.fit}): {text}")

    response = client.models.generate_content(
        model=MODEL,
        contents=INSTRUCTIONS + "\n\nReviews:\n" + "\n".join(lines),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA,
            temperature=0,
        ),
    )
    return json.loads(response.text)


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY is not set, skipping the Gemini review tagging step.")
        return
    if os.path.exists(TAGS_PATH):
        print("Reasons already tagged:", TAGS_PATH, "(delete it to tag again)")
        return

    # Imported here so the rest of the project runs without this package.
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    sample = sample_misfits()
    tags = []

    for start in range(0, len(sample), BATCH_SIZE):
        batch = sample.iloc[start:start + BATCH_SIZE]
        try:
            tags += tag_batch(client, types, batch)
        except Exception as error:  # e.g. rate limit: wait, then try once more
            print("  request failed, retrying in 60s:", error)
            time.sleep(60)
            tags += tag_batch(client, types, batch)
        print(f"  tagged {min(start + BATCH_SIZE, len(sample))}/{len(sample)}")
        time.sleep(PAUSE_SECONDS)

    # Join the reasons back onto the sampled reviews.
    reasons = pd.DataFrame(tags).rename(columns={"id": "review_id"}).drop_duplicates("review_id")
    tagged = sample.merge(reasons, on="review_id", how="inner")
    print(f"Gemini returned a reason for {len(tagged)} of {len(sample)} reviews")

    tagged[["review_id", "fit", "category", "reason"]].to_csv(TAGS_PATH, index=False)

    summary = tagged.groupby("reason").size().reset_index(name="reviews")
    summary["share_pct"] = (100 * summary["reviews"] / summary["reviews"].sum()).round(1)
    summary = summary.sort_values("reviews", ascending=False)
    summary.to_csv(SUMMARY_PATH, index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

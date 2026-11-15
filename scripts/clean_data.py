"""Step 2: clean the raw reviews with pandas.

Every row we remove is counted in outputs/cleaning_log.csv together with the
reason. Values we fix (but keep the row) are logged there too.

Output: data/clean_reviews.csv
"""
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(ROOT, "data", "raw", "renttherunway_final_data.json.gz")
CLEAN_PATH = os.path.join(ROOT, "data", "clean_reviews.csv")
LOG_PATH = os.path.join(ROOT, "outputs", "cleaning_log.csv")

# A few categories appear in both singular and plural form. Merge them.
CATEGORY_FIXES = {
    "pant": "pants",
    "legging": "leggings",
    "culotte": "culottes",
    "trouser": "trousers",
    "skirts": "skirt",
    "caftan": "kaftan",
    "sweatershirt": "sweatshirt",
}

log = []  # one entry per cleaning step


def log_step(step, action, rows, reason):
    """Remember what a cleaning step did, and print it."""
    log.append({"step": step, "action": action, "rows": rows, "reason": reason})
    print(f"  {action:<16} {rows:>7,}  {reason}")


def remove(df, mask, step, reason):
    """Drop the rows where mask is True and log how many went."""
    log_step(step, "removed", int(mask.sum()), reason)
    return df[~mask].copy()


def height_to_inches(text):
    """Turn a height like 5' 8" into 68 (inches). Missing stays missing."""
    if pd.isna(text):
        return None
    feet, inches = text.replace('"', "").split("'")
    return int(feet) * 12 + int(inches)


def main():
    df = pd.read_json(RAW_PATH, lines=True)
    log_step("raw", "loaded", len(df), "rows in the raw file")

    # 1. Tidy column names: "bust size" -> "bust_size"
    df.columns = [c.replace(" ", "_") for c in df.columns]

    # 2. Remove duplicates.
    # Exact copies of a row (every column the same).
    df = remove(df, df.astype(str).duplicated(), "duplicates", "exact duplicate row")
    # The same review (same user, item, date and text) posted twice.
    same_review = df.duplicated(["user_id", "item_id", "review_date", "review_text"])
    df = remove(df, same_review, "duplicates", "same user, item, date and text as another review")

    # 3. Remove rows without a rating (needed for the rating comparison).
    df = remove(df, df["rating"].isna(), "missing", "rating is missing")

    # 4. Fix types.
    # Rating is stored as 2, 4, 6, 8, 10. Divide by 2 to get 1-5 stars.
    df["rating"] = (df["rating"] / 2).astype(int)
    df["review_date"] = pd.to_datetime(df["review_date"], format="%B %d, %Y")
    df["user_id"] = df["user_id"].astype(str)
    df["item_id"] = df["item_id"].astype(str)

    # 5. Parse body measurements into numbers.
    df["height_in"] = df["height"].apply(height_to_inches)              # 5' 8" -> 68
    df["weight_lbs"] = df["weight"].str.replace("lbs", "").astype(float)  # "137lbs" -> 137
    bust = df["bust_size"].str.extract(r"^(\d+)(.*)$")                  # "34d" -> 34, "d"
    df["bust_band"] = bust[0].astype(float)
    df["cup_size"] = bust[1]

    # 6. Ages under 18 or over 90 are almost certainly typing errors
    #    (the raw file has ages of 0 and 117). Keep the review, blank the age.
    bad_age = (df["age"] < 18) | (df["age"] > 90)
    log_step("fix", "age set missing", int(bad_age.sum()), "age under 18 or over 90")
    df.loc[bad_age, "age"] = None

    # 7. Merge singular/plural category names.
    to_fix = df["category"].isin(CATEGORY_FIXES.keys())
    log_step("fix", "category merged", int(to_fix.sum()), "singular/plural names merged (e.g. pant -> pants)")
    df["category"] = df["category"].replace(CATEGORY_FIXES)

    # "party: cocktail" appears once; treat it as "party".
    df["rented_for"] = df["rented_for"].replace({"party: cocktail": "party"})

    # 8. Keep the columns we need, in a sensible order.
    df = df[[
        "user_id", "item_id", "category", "size", "fit", "rating", "rented_for",
        "body_type", "height_in", "weight_lbs", "bust_band", "cup_size", "age",
        "review_date", "review_summary", "review_text",
    ]]
    df.insert(0, "review_id", range(1, len(df) + 1))

    log_step("clean", "kept", len(df), "rows in the clean table")

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    pd.DataFrame(log).to_csv(LOG_PATH, index=False)
    df.to_csv(CLEAN_PATH, index=False)
    print("Saved", CLEAN_PATH)


if __name__ == "__main__":
    main()

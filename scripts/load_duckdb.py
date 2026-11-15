"""Step 3: load the clean reviews into a DuckDB database file.

Output: data/fit.duckdb with one table, reviews (one row per review).
"""
import os

import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH = os.path.join(ROOT, "data", "clean_reviews.csv")
DB_PATH = os.path.join(ROOT, "data", "fit.duckdb")


def main():
    con = duckdb.connect(DB_PATH)

    # DuckDB reads the CSV directly and guesses each column's type.
    con.execute(f"""
        CREATE OR REPLACE TABLE reviews AS
        SELECT * FROM read_csv('{CLEAN_PATH}', header = true,
                               types = {{'user_id': 'VARCHAR', 'item_id': 'VARCHAR'}})
    """)

    rows = con.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    items = con.execute("SELECT COUNT(DISTINCT item_id) FROM reviews").fetchone()[0]
    users = con.execute("SELECT COUNT(DISTINCT user_id) FROM reviews").fetchone()[0]
    print(f"Loaded {rows:,} reviews of {items:,} items by {users:,} users into {DB_PATH}")
    con.close()


if __name__ == "__main__":
    main()

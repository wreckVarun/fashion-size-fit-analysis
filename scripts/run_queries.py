"""Step 4: run every .sql file in sql/ against DuckDB and save the results.

Each query's result is saved as outputs/<query name>.csv and the first rows
are printed so you can read them in the terminal.
"""
import glob
import os

import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "data", "fit.duckdb")
SQL_DIR = os.path.join(ROOT, "sql")
OUT_DIR = os.path.join(ROOT, "outputs")


def main():
    con = duckdb.connect(DB_PATH, read_only=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    for sql_path in sorted(glob.glob(os.path.join(SQL_DIR, "*.sql"))):
        name = os.path.splitext(os.path.basename(sql_path))[0]
        with open(sql_path) as f:
            query = f.read()

        result = con.execute(query).df()  # run the query, get a pandas table
        result.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)

        print(f"\n== {name} ({len(result)} rows)")
        print(result.head(12).to_string(index=False))

    con.close()


if __name__ == "__main__":
    main()

"""Run the whole project with one command:  python3 run_all.py

1. download the raw reviews
2. clean them with pandas (every removal is logged)
3. load the clean table into DuckDB
4. run every SQL query in sql/ and save the results to outputs/
5. (optional) tag 500 misfit reviews by reason with Gemini, if GEMINI_API_KEY is set
6. build the dashboard at docs/index.html
"""
import os
import sys

# Let Python find the scripts in the scripts/ folder.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))

import build_dashboard  # noqa: E402
import clean_data  # noqa: E402
import download_data  # noqa: E402
import load_duckdb  # noqa: E402
import run_queries  # noqa: E402
import tag_reasons  # noqa: E402

if __name__ == "__main__":
    print("\n[1/6] Download data")
    download_data.main()
    print("\n[2/6] Clean data")
    clean_data.main()
    print("\n[3/6] Load into DuckDB")
    load_duckdb.main()
    print("\n[4/6] Run SQL queries")
    run_queries.main()
    print("\n[5/6] Tag misfit reasons with Gemini (optional)")
    tag_reasons.main()
    print("\n[6/6] Build dashboard")
    build_dashboard.main()
    print("\nDone. Open docs/index.html in a browser.")

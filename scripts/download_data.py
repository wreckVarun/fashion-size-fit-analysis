"""Step 1: download the RentTheRunway reviews from the Clothing Fit Dataset.

The dataset is listed on Kaggle as "Clothing Fit Dataset for Size
Recommendation" (rmisra). Kaggle only serves it to logged-in users, so we
download the same file from the dataset authors' own host at UC San Diego,
which needs no account.

The file is saved to data/raw/renttherunway_final_data.json.gz (about 31 MB).
"""
import os
import urllib.request

# Project folder = the folder above this scripts/ folder.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_URL = "https://mcauleylab.ucsd.edu/public_datasets/data/renttherunway/renttherunway_final_data.json.gz"
RAW_DIR = os.path.join(ROOT, "data", "raw")
RAW_PATH = os.path.join(RAW_DIR, "renttherunway_final_data.json.gz")


def main():
    os.makedirs(RAW_DIR, exist_ok=True)

    # Skip the download if we already have the file.
    if os.path.exists(RAW_PATH):
        print("Raw data already present:", RAW_PATH)
        return

    print("Downloading RentTheRunway reviews...")
    urllib.request.urlretrieve(DATASET_URL, RAW_PATH)

    size_mb = os.path.getsize(RAW_PATH) / 1_000_000
    print(f"Saved {RAW_PATH} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()

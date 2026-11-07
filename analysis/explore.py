import json
from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "records.json"

with open(DATA_FILE, "r", encoding="utf-8") as file:
    records = json.load(file)

if isinstance(records, dict):
    records = records.get("records", [])

df = pd.DataFrame(records)

if df.empty:
    print("No records found.")
else:
    print("\n===== SAMVIDHANSATHI DATA EXPLORATION =====")

    # Fact 1: Total records
    print("\n1. Total Constitution records:")
    print(len(df))

    # Fact 2: Records per Part
    print("\n2. Number of records in each Part:")
    print(df["part"].value_counts().to_string())

    # Fact 3: Longest article text
    df["text_length"] = df["text"].fillna("").astype(str).str.len()
    longest = df.loc[df["text_length"].idxmax()]

    print("\n3. Article with the longest text:")
    print("Article:", longest["article_no"])
    print("Title:", longest["title"])
    print("Characters:", longest["text_length"])

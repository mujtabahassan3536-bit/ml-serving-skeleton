from pathlib import Path

import pandas as pd

RAW_PATH = Path("data/zameen_raw.csv")


def audit_raw() -> None:
    df = pd.read_csv(RAW_PATH, sep=";")

    print("=== 1. TOP 10 CITIES ===")
    print(df["city"].value_counts().head(10))

    print("\n=== 2. PURPOSE & PROPERTY TYPE ===")
    print(df["purpose"].value_counts())
    print("\n", df["property_type"].value_counts())

    print("\n=== 3. AREA UNITS CHECK ===")
    units = df["area"].astype(str).str.split().str[-1].value_counts()
    print(units)

    print("\n=== 4. PRICE ANOMALIES & DUPLICATES ===")
    print(f"Exact row duplicates: {df.duplicated().sum()}")
    print(f"Duplicate property_id: {df['property_id'].duplicated().sum()}")
    print(f"Price <= 10,000 PKR: {(df['price'] <= 10_000).sum()}")
    print(f"Price >= 1,000,000,000 (1 Arab): {(df['price'] >= 1_000_000_000).sum()}")

    houses = df[df["property_type"] == "House"]
    print(f"\n=== 5. HIDDEN ZEROS IN HOUSES (Total Houses: {len(houses)}) ===")
    print(f"Houses with 0 bedrooms: {(houses['bedrooms'] == 0).sum()}")
    print(f"Houses with 0 baths: {(houses['baths'] == 0).sum()}")


if __name__ == "__main__":
    audit_raw()

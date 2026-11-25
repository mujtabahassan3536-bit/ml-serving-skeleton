from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "dataset.csv"


def load_and_clean_data() -> tuple[pd.DataFrame, int, int]:
    df = pd.read_csv(DATA_PATH)
    raw_rows = len(df)
    df = df.drop_duplicates()
    df["city"] = (
        df["city"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({"fsd": "faisalabad", "lhr": "lahore", "isb": "islamabad"})
    )
    df = df[df["city"].isin(["faisalabad", "lahore", "islamabad"])]

    df["area_sqft"] = pd.to_numeric(
        df["area_sqft"]
        .astype(str)
        .str.replace("sqft", "", case=False)
        .str.replace(",", "")
        .str.strip(),
        errors="coerce",
    )

    df["bedrooms"] = pd.to_numeric(
        df["bedrooms"]
        .astype(str)
        .str.replace("beds", "", case=False)
        .str.replace(",", "")
        .str.strip(),
        errors="coerce",
    )

    df["age_years"] = pd.to_numeric(df["age_years"], errors="coerce")

    df["price"] = pd.to_numeric(
        df["price"]
        .astype(str)
        .str.replace("pkr", "", case=False)
        .str.replace(",", "")
        .str.strip(),
        errors="coerce",
    )

    df = df.dropna(subset=["city", "area_sqft", "bedrooms", "age_years", "price"])

    df = df[
        (df["area_sqft"] > 200)
        & (df["area_sqft"] <= 50000)
        & (df["bedrooms"] >= 1)
        & (df["bedrooms"] <= 20)
        & (df["age_years"] >= 0)
        & (df["age_years"] <= 100)
        & (df["price"] >= 500000)
        & (df["price"] <= 500000000)
    ]

    return df, raw_rows, len(df)


def predict_price(
    city: str, area_sqft: float, bedrooms: int, age_years: int
) -> tuple[float, float]:
    df, _, _ = load_and_clean_data()
    city_df = df[df["city"] == city]
    avg_ppsqft = float((city_df["price"] / city_df["area_sqft"]).mean())
    estimated = max(
        area_sqft * avg_ppsqft + bedrooms * 300_000 - age_years * 40_000, 500_000.0
    )
    return round(estimated, 2), round(avg_ppsqft, 2)

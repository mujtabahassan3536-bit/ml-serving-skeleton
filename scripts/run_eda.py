import json
from pathlib import Path
from typing import Any, cast

import matplotlib.pyplot as plt  # type: ignore[import-untyped]
import numpy as np
import pandas as pd

RAW_PATH = Path("data/zameen_raw.csv")
CLEAN_PATH = Path("data/zameen_clean.csv")
REPORTS_DIR = Path("reports")
FIGURES_DIR = REPORTS_DIR / "figures"

UNIT_TO_SQFT = {"kanal": 4500.0, "marla": 225.0}


def clean_zameen_houses(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    funnel = {"raw_rows": len(raw_df)}

    # Keep only residential houses listed for sale
    is_house_sale = (raw_df["purpose"] == "For Sale") & (
        raw_df["property_type"] == "House"
    )
    df = raw_df.loc[is_house_sale].copy()
    funnel["houses_for_sale"] = len(df)

    for col in ("price", "bedrooms", "baths"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Normalize area strings like "6 Kanal" or "1,200 Marla" into square feet
    area_tokens = df["area"].astype(str).str.strip().str.split()
    area_val = pd.to_numeric(
        area_tokens.str[0].str.replace(",", "", regex=False), errors="coerce"
    )
    area_unit = area_tokens.str[-1].str.lower()
    df["area_sqft"] = area_val * area_unit.map(UNIT_TO_SQFT)

    # Filter out placeholder prices (< 10 Lac) and extreme outliers (> 100 Cr or > 10 Kanal)
    valid_bounds = df["price"].between(1_000_000, 1_000_000_000) & df[
        "area_sqft"
    ].between(225.0, 45_000.0)
    df = df.loc[valid_bounds].copy()
    funnel["valid_price_area"] = len(df)

    # Zameen uses 0 when bedroom/bath counts aren't filled in by the agent
    df[["bedrooms", "baths"]] = df[["bedrooms", "baths"]].replace(0, np.nan)

    cols = ["city", "location", "area_sqft", "bedrooms", "baths", "price"]
    df = df.drop_duplicates(subset=cols).copy()
    funnel["deduplicated"] = len(df)

    return df[cols], funnel


def summarize_dataset(df: pd.DataFrame, funnel: dict[str, int]) -> dict[str, Any]:
    sqft_rate = df["price"] / df["area_sqft"]
    by_city = (
        df.groupby("city", observed=True)
        .agg(
            listings=("price", "count"),
            median_price_pkr=("price", "median"),
            median_area_sqft=("area_sqft", "median"),
        )
        .sort_values("listings", ascending=False)
        .to_dict(orient="index")
    )

    return {
        "funnel": funnel,
        "retention_pct": round(len(df) / funnel["raw_rows"] * 100, 2),
        "missing_counts": {col: int(cnt) for col, cnt in df.isna().sum().items()},
        "price_skew_raw": round(cast(float, df["price"].skew()), 3),
        "price_skew_log1p": round(float(np.log1p(df["price"]).skew()), 3),
        "median_price_per_sqft_pkr": round(float(sqft_rate.median()), 2),
        "city_breakdown": by_city,
    }


def plot_price_distributions(df: pd.DataFrame, out_dir: Path) -> None:
    plt.switch_backend("Agg")
    out_dir.mkdir(parents=True, exist_ok=True)

    fig, (ax_raw, ax_log) = plt.subplots(1, 2, figsize=(12, 5))

    ax_raw.hist(df["price"] / 1e7, bins=50, color="steelblue", edgecolor="white")
    ax_raw.set(
        title="Raw House Prices (Crore PKR)",
        xlabel="Price (Crore PKR)",
        ylabel="Listings",
    )

    ax_log.hist(np.log1p(df["price"]), bins=50, color="seagreen", edgecolor="white")
    ax_log.set(
        title="Log-Transformed Prices",
        xlabel="log1p(Price PKR)",
        ylabel="Listings",
    )

    fig.tight_layout()
    fig.savefig(out_dir / "price_distribution.png", dpi=150)
    plt.close(fig)


def main() -> None:
    raw_df = pd.read_csv(RAW_PATH, sep=";")
    clean_df, funnel = clean_zameen_houses(raw_df)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(CLEAN_PATH, index=False)

    summary = summarize_dataset(clean_df, funnel)
    (REPORTS_DIR / "eda_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    plot_price_distributions(clean_df, FIGURES_DIR)

    print("Cleaning funnel:")
    for step, count in funnel.items():
        print(f"  {step}: {count:,}")
    print(
        f"\nSkewness (raw -> log1p): "
        f"{summary['price_skew_raw']} -> {summary['price_skew_log1p']}"
    )
    print("Missing values:", summary["missing_counts"])


if __name__ == "__main__":
    main()
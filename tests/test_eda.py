import json

import pandas as pd

from scripts.run_eda import clean_zameen_houses, summarize_dataset


def test_clean_zameen_houses_filters_and_normalizes() -> None:
    raw = pd.DataFrame(
        [
            {
                "purpose": "For Sale",
                "property_type": "House",
                "city": "Lahore",
                "location": "DHA Phase 6",
                "area": "6 Kanal",
                "bedrooms": 0,
                "baths": 6,
                "price": 220_000_000,
            },
            {
                "purpose": "For Sale",
                "property_type": "House",
                "city": "Lahore",
                "location": "DHA Phase 6",
                "area": "6 Kanal",
                "bedrooms": 0,
                "baths": 6,
                "price": 220_000_000,
            },
            {
                "purpose": "For Sale",
                "property_type": "House",
                "city": "Islamabad",
                "location": "F-10",
                "area": "10 Marla",
                "bedrooms": 4,
                "baths": 4,
                "price": 65_000_000,
            },
            {
                "purpose": "For Sale",
                "property_type": "House",
                "city": "Karachi",
                "location": "Clifton",
                "area": "1,200 Marla",
                "bedrooms": 5,
                "baths": 5,
                "price": 150_000_000,
            },
            {
                "purpose": "For Sale",
                "property_type": "House",
                "city": "Lahore",
                "location": "Johar Town",
                "area": "5 Marla",
                "bedrooms": 3,
                "baths": 3,
                "price": 5_000,
            },
            {
                "purpose": "For Rent",
                "property_type": "House",
                "city": "Lahore",
                "location": "Model Town",
                "area": "10 Marla",
                "bedrooms": 3,
                "baths": 3,
                "price": 85_000,
            },
            {
                "purpose": "For Sale",
                "property_type": "Flat",
                "city": "Karachi",
                "location": "Gulshan-e-Iqbal",
                "area": "5 Marla",
                "bedrooms": 2,
                "baths": 2,
                "price": 12_000_000,
            },
        ]
    )

    clean_df, funnel = clean_zameen_houses(raw)

    assert funnel == {
        "raw_rows": 7,
        "houses_for_sale": 5,
        "valid_price_area": 3,
        "deduplicated": 2,
    }
    assert len(clean_df) == 2
    assert clean_df.iloc[0]["area_sqft"] == 27000.0
    assert pd.isna(clean_df.iloc[0]["bedrooms"])
    assert clean_df.iloc[0]["baths"] == 6.0
    assert clean_df.iloc[1]["area_sqft"] == 2250.0


def test_summarize_dataset_is_json_serializable() -> None:
    raw = pd.DataFrame(
        [
            {
                "purpose": "For Sale",
                "property_type": "House",
                "city": "Lahore",
                "location": "DHA Phase 6",
                "area": "1 Kanal",
                "bedrooms": 0,
                "baths": 5,
                "price": 55_000_000,
            },
            {
                "purpose": "For Sale",
                "property_type": "House",
                "city": "Lahore",
                "location": "Bahria Town",
                "area": "10 Marla",
                "bedrooms": 4,
                "baths": 4,
                "price": 32_000_000,
            },
        ]
    )

    clean_df, funnel = clean_zameen_houses(raw)
    summary = summarize_dataset(clean_df, funnel)

    encoded = json.dumps(summary)
    assert isinstance(encoded, str)
    assert summary["retention_pct"] == 100.0
    assert summary["missing_counts"]["bedrooms"] == 1
    assert summary["city_breakdown"]["Lahore"]["listings"] == 2
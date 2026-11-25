import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 1000

cities = rng.choice(
    [
        "Faisalabad",
        " faisalabad ",
        "FAISALABAD",
        "fsd",
        "Lahore",
        "lhr",
        "LAHORE",
        "Islamabad",
        "isb",
        " unknown ",
        None,
    ],
    size=n,
    p=[0.15, 0.08, 0.07, 0.05, 0.15, 0.08, 0.07, 0.15, 0.08, 0.06, 0.06],
)
areas = rng.integers(500, 5000, size=n).astype(object)
bedrooms = rng.integers(1, 8, size=n).astype(object)
ages = rng.integers(0, 35, size=n).astype(object)

base_rate = np.where(
    pd.Series(cities).fillna("").str.lower().str.contains("isb|islamabad"),
    11000,
    np.where(
        pd.Series(cities).fillna("").str.lower().str.contains("lhr|lahore"), 9500, 7000
    ),
)
prices = (
    areas.astype(float) * base_rate
    + bedrooms.astype(float) * 300000
    - ages.astype(float) * 40000
).astype(object)

# Inject real-world data corruption
for i in rng.choice(n, size=120, replace=False):
    areas[i] = f"{areas[i]:,} sqft"
for i in rng.choice(n, size=100, replace=False):
    prices[i] = f"PKR {int(prices[i]):,}"
for i in rng.choice(n, size=45, replace=False):
    areas[i] = rng.choice(["N/A", "-450", "", None])
for i in rng.choice(n, size=45, replace=False):
    prices[i] = rng.choice(["invalid", "0", "99999999999", None])
for i in rng.choice(n, size=35, replace=False):
    bedrooms[i] = rng.choice(["3 beds", "0", "-2", None])
for i in rng.choice(n, size=35, replace=False):
    ages[i] = rng.choice(["-5", "unknown", None])

df = pd.DataFrame(
    {
        "city": cities,
        "area_sqft": areas,
        "bedrooms": bedrooms,
        "age_years": ages,
        "price": prices,
    }
)
# Add 50 duplicate rows
df = pd.concat([df, df.sample(50, random_state=42)], ignore_index=True)
df.to_csv("data/dataset.csv", index=False)
print(f"Generated messy dataset with {len(df)} rows!")

"""
PropIntel AI — Synthetic Property Dataset Generator
====================================================
Generates 500 realistic Indian property records across 5 cities
with pricing, market signals, proximity features, and fraud labels.

Usage:
    python data/generate_data.py
"""

import pandas as pd
import numpy as np
import random
import os

# ──────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────

CITIES = ["Pune", "Mumbai", "Bangalore", "Hyderabad", "Chennai"]

CITY_META = {
    "Pune": {
        "lat_range": (18.4, 18.7),
        "lon_range": (73.7, 73.9),
        "pincode_range": (411001, 411028),
        "circle_rate": (6000, 15000),
    },
    "Mumbai": {
        "lat_range": (18.9, 19.3),
        "lon_range": (72.7, 73.0),
        "pincode_range": (400001, 400072),
        "circle_rate": (12000, 35000),
    },
    "Bangalore": {
        "lat_range": (12.8, 13.2),
        "lon_range": (77.4, 77.7),
        "pincode_range": (560001, 560103),
        "circle_rate": (8000, 20000),
    },
    "Hyderabad": {
        "lat_range": (17.2, 17.7),
        "lon_range": (78.3, 78.7),
        "pincode_range": (500001, 500075),
        "circle_rate": (5000, 14000),
    },
    "Chennai": {
        "lat_range": (12.9, 13.2),
        "lon_range": (80.1, 80.4),
        "pincode_range": (600001, 600119),
        "circle_rate": (6000, 16000),
    },
}

PROPERTY_TYPES = ["Apartment", "Villa", "Independent House"]

# BHK distribution probabilities
BHK_PROBS = {1: 0.10, 2: 0.45, 3: 0.35, 4: 0.10}

# Size ranges per BHK (sqft)
SIZE_RANGES = {
    1: (400, 700),
    2: (800, 1400),
    3: (1300, 2200),
    4: (2000, 4000),
}


# ──────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────

def weighted_choice(choices: dict) -> int:
    """Return a key from *choices* where values are probabilities."""
    keys = list(choices.keys())
    probs = list(choices.values())
    return int(np.random.choice(keys, p=probs))


def random_locality(city: str) -> str:
    """Return a plausible locality name for the given city."""
    localities = {
        "Pune": ["Baner", "Hinjewadi", "Kothrud", "Wakad", "Hadapsar",
                 "Viman Nagar", "Aundh", "Pimpri", "Kharadi", "Magarpatta"],
        "Mumbai": ["Andheri", "Bandra", "Powai", "Thane", "Worli",
                   "Goregaon", "Malad", "Borivali", "Kandivali", "Chembur"],
        "Bangalore": ["Whitefield", "Koramangala", "Electronic City",
                      "HSR Layout", "Indiranagar", "Marathahalli",
                      "Bellandur", "Sarjapur", "Hebbal", "JP Nagar"],
        "Hyderabad": ["Gachibowli", "Madhapur", "Kondapur", "Miyapur",
                      "Kukatpally", "Begumpet", "Ameerpet", "HITEC City",
                      "Banjara Hills", "Secunderabad"],
        "Chennai": ["Adyar", "T Nagar", "Velachery", "OMR", "Anna Nagar",
                    "Porur", "Tambaram", "Chromepet", "Sholinganallur",
                    "Guindy"],
    }
    return random.choice(localities.get(city, [f"{city} Locality"]))


def compute_target_price(p: dict) -> float:
    """Compute actual_price_sqft from the formula specified in the brief."""
    cr = p["circle_rate_sqft"]
    base = cr * 1.18

    location_boost = max(0, (6 - p["metro_distance_km"])) * 380
    connectivity_boost = max(0, (8 - p["highway_distance_km"])) * 220
    age_penalty = p["age_years"] * 130
    floor_premium = p["floor"] * 75
    govt_boost = p["govt_project_nearby"] * 950
    npa_penalty = p["npa_zone"] * 600
    builder_premium = (p["builder_score"] - 60) * 18
    supply_penalty = max(0, (p["supply_demand_ratio"] - 1.0) * 400)
    trend_boost = base * (p["price_trend_6m"] / 100)
    noise = np.random.normal(0, 480)

    price = (
        base
        + location_boost
        + connectivity_boost
        + floor_premium
        + govt_boost
        + builder_premium
        + trend_boost
        - age_penalty
        - npa_penalty
        - supply_penalty
        + noise
    )

    # Clamp to statutory bounds and round to nearest 50
    lower = cr * 0.85
    upper = cr * 3.5
    price = max(lower, min(upper, price))
    price = round(price / 50) * 50
    return float(price)


def generate_row() -> dict:
    """Generate a single synthetic property record."""
    city = random.choice(CITIES)
    meta = CITY_META[city]
    locality = random_locality(city)
    pincode = random.randint(*meta["pincode_range"])
    latitude = round(random.uniform(*meta["lat_range"]), 6)
    longitude = round(random.uniform(*meta["lon_range"]), 6)

    property_type = random.choice(PROPERTY_TYPES)
    bhk = weighted_choice(BHK_PROBS)
    sqft = random.randint(*SIZE_RANGES[bhk])
    age_years = random.randint(0, 30)
    floor = random.randint(1, 25)
    total_floors = floor + random.randint(1, 10)
    has_lift = (0 if random.random() < 0.1 else 1) if total_floors > 4 else random.randint(0, 1)
    ownership_type = "freehold" if random.random() < 0.8 else "leasehold"
    circle_rate_sqft = random.randint(*meta["circle_rate"])

    days_on_market = random.randint(10, 180)
    listing_count = random.randint(20, 500)
    metro_distance_km = round(np.random.beta(2, 2) * 11.8 + 0.2, 2)
    highway_distance_km = round(0.5 + random.random() * 14.5, 2)
    it_park_distance_km = round(0.5 + random.random() * 19.5, 2)
    school_distance_km = round(0.1 + random.random() * 7.9, 2)
    hospital_distance_km = round(0.2 + random.random() * 7.8, 2)

    builder_score = random.randint(40, 95)
    govt_project_nearby = random.randint(0, 1)
    npa_zone = random.randint(0, 1)
    supply_demand_ratio = round(random.uniform(0.4, 2.5), 2)
    price_trend_6m = round(random.uniform(-8, 15), 1)
    absorption_rate = round(random.uniform(0.03, 0.40), 2)

    actual_price_sqft = compute_target_price({
        "circle_rate_sqft": circle_rate_sqft,
        "metro_distance_km": metro_distance_km,
        "highway_distance_km": highway_distance_km,
        "age_years": age_years,
        "floor": floor,
        "govt_project_nearby": govt_project_nearby,
        "npa_zone": npa_zone,
        "builder_score": builder_score,
        "supply_demand_ratio": supply_demand_ratio,
        "price_trend_6m": price_trend_6m,
    })

    return {
        "city": city,
        "locality": locality,
        "pincode": pincode,
        "latitude": latitude,
        "longitude": longitude,
        "property_type": property_type,
        "bhk": bhk,
        "sqft": sqft,
        "age_years": age_years,
        "floor": floor,
        "total_floors": total_floors,
        "has_lift": has_lift,
        "ownership_type": ownership_type,
        "circle_rate_sqft": circle_rate_sqft,
        "days_on_market": days_on_market,
        "listing_count": listing_count,
        "metro_distance_km": metro_distance_km,
        "highway_distance_km": highway_distance_km,
        "it_park_distance_km": it_park_distance_km,
        "school_distance_km": school_distance_km,
        "hospital_distance_km": hospital_distance_km,
        "builder_score": builder_score,
        "govt_project_nearby": govt_project_nearby,
        "npa_zone": npa_zone,
        "supply_demand_ratio": supply_demand_ratio,
        "price_trend_6m": price_trend_6m,
        "absorption_rate": absorption_rate,
        "actual_price_sqft": actual_price_sqft,
        "fraud_flag": 0,
    }


def inject_fraud(df: pd.DataFrame) -> pd.DataFrame:
    """Inject 3 mandatory fraud rows at indices 497-499 (rows 498-500)."""
    # Row 498 (idx 497): SIZE ANOMALY — 2BHK but 4200 sqft
    df.at[497, "bhk"] = 2
    df.at[497, "sqft"] = 4200
    df.at[497, "fraud_flag"] = 1

    # Row 499 (idx 498): TYPE ANOMALY — mismatch property type
    current_type = df.at[498, "property_type"]
    others = [t for t in PROPERTY_TYPES if t != current_type]
    df.at[498, "property_type"] = random.choice(others)
    df.at[498, "fraud_flag"] = 1

    # Row 500 (idx 499): AGE ANOMALY — age 1 but price at lower bound
    df.at[499, "age_years"] = 1
    cr = df.at[499, "circle_rate_sqft"]
    df.at[499, "actual_price_sqft"] = round(cr * 0.85 / 50) * 50
    df.at[499, "fraud_flag"] = 1

    return df


def print_summary(df: pd.DataFrame) -> None:
    """Print dataset statistics to console."""
    print("\n" + "=" * 60)
    print("  SYNTHETIC DATASET SUMMARY")
    print("=" * 60)

    # Mean & median price per city
    stats = df.groupby("city")["actual_price_sqft"].agg(["mean", "median"]).round(2)
    print("\n[PRICE] Mean & Median price per city (Rs/sqft):")
    print(stats.to_string())

    # BHK distribution
    bhk_dist = df["bhk"].value_counts().sort_index()
    print("\n[BHK] Distribution:")
    for bhk, count in bhk_dist.items():
        pct = count / len(df) * 100
        print(f"  {bhk}BHK: {count} ({pct:.1f}%)")

    # Price histogram
    hist, bins = np.histogram(df["actual_price_sqft"], bins=10)
    print("\n[HIST] Price histogram (Rs/sqft buckets):")
    for i in range(len(hist)):
        bar = "#" * max(1, hist[i] // 3)
        print(f"  {int(bins[i]):>6} - {int(bins[i+1]):>6}: {hist[i]:>3}  {bar}")

    # Top 5 correlations
    numeric = [c for c in df.columns
               if pd.api.types.is_numeric_dtype(df[c]) and c != "actual_price_sqft"]
    corr = (df[numeric + ["actual_price_sqft"]]
            .corr()["actual_price_sqft"]
            .drop("actual_price_sqft")
            .abs()
            .sort_values(ascending=False)
            .head(5))
    print("\n[CORR] Top 5 features correlated with price:")
    for feat, val in corr.items():
        print(f"  {feat:<25} {val:.4f}")

    # Fraud count
    fraud_count = int(df["fraud_flag"].sum())
    print(f"\n[FRAUD] Fraud rows: {fraud_count}")
    print(f"[TOTAL] Total rows: {len(df)}")
    print("=" * 60)


def generate_dataset(num_rows: int = 500, output_path: str = None) -> None:
    """Generate the full synthetic dataset and save to CSV."""
    np.random.seed(42)
    random.seed(42)

    rows = [generate_row() for _ in range(num_rows)]
    df = pd.DataFrame(rows)
    df = inject_fraud(df)

    print_summary(df)

    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "synthetic_properties.csv")
    df.to_csv(output_path, index=False)
    print(f"\n[SUCCESS] Dataset saved -> {output_path} ({len(df)} rows)")


if __name__ == "__main__":
    generate_dataset()

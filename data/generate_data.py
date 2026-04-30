import pandas as pd
import numpy as np
import random
import os
from pathlib import Path

# ---------- CONFIGURATION ----------
CITIES = ["Pune", "Mumbai", "Bangalore", "Hyderabad", "Chennai"]

# Basic city metadata (approximate latitude, longitude, pincode range)
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

# BHK distribution probabilities (must sum to 1)
BHK_PROBS = {
    1: 0.10,
    2: 0.45,
    3: 0.35,
    4: 0.10,
}

# Size ranges per BHK (sqft)
SIZE_RANGES = {
    1: (400, 700),
    2: (800, 1400),
    3: (1300, 2200),
    4: (2000, 4000),
}

# Helper functions -------------------------------------------------

def weighted_choice(choices: dict):
    """Return a key from a dict where values are probabilities (summing to 1)."""
    items = list(choices.items())
    keys, probs = zip(*items)
    return np.random.choice(keys, p=probs)

def random_city_meta():
    city = random.choice(CITIES)
    meta = CITY_META[city]
    return city, meta

def random_locality(city: str) -> str:
    return f"{city} Locality {random.randint(1, 50)}"

def random_pincode(meta: dict) -> int:
    return random.randint(meta["pincode_range"][0], meta["pincode_range"][1])

def random_lat_lon(meta: dict) -> tuple:
    lat = round(random.uniform(*meta["lat_range"]), 6)
    lon = round(random.uniform(*meta["lon_range"]), 6)
    return lat, lon

def sample_bhk():
    return weighted_choice(BHK_PROBS)

def sample_size(bhk):
    low, high = SIZE_RANGES[bhk]
    return random.randint(low, high)

def sample_property_type():
    return random.choice(PROPERTY_TYPES)

def sample_floor_and_total():
    floor = random.randint(1, 25)
    total_floors = floor + random.randint(1, 10)
    return floor, total_floors

def sample_has_lift(total_floors):
    if total_floors > 4:
        return 0 if random.random() < 0.1 else 1
    else:
        return random.randint(0, 1)

def sample_ownership():
    return "freehold" if random.random() < 0.8 else "leasehold"

def sample_circle_rate(city):
    low, high = CITY_META[city]["circle_rate"]
    return random.randint(low, high)

def sample_proximity():
    metro = round(np.random.beta(2, 2) * 11.8 + 0.2, 2)  # 0.2‑12 km, skewed toward 1‑6
    highway = round(0.5 + random.random() * 14.5, 2)   # 0.5‑15 km
    return metro, highway

def compute_target_price(params: dict) -> float:
    cr = params["circle_rate_sqft"]
    base = cr * 1.18
    location_boost = max(0, (6 - params["metro_distance_km"])) * 380
    connectivity_boost = max(0, (8 - params["highway_distance_km"])) * 220
    age_penalty = params["age_years"] * 130
    floor_premium = params["floor"] * 75
    govt_boost = params["govt_project_nearby"] * 950
    npa_penalty = params["npa_zone"] * 600
    builder_premium = (params["builder_score"] - 60) * 18
    supply_penalty = max(0, (params["supply_demand_ratio"] - 1.0) * 400)
    trend_boost = base * (params["price_trend_6m"] / 100)
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
    lower = cr * 0.85
    upper = cr * 3.5
    price = max(lower, min(upper, price))
    price = round(price / 50) * 50
    return price

def generate_row(row_idx: int) -> dict:
    city, meta = random_city_meta()
    locality = random_locality(city)
    pincode = random_pincode(meta)
    latitude, longitude = random_lat_lon(meta)
    property_type = sample_property_type()
    bhk = sample_bhk()
    size_sqft = sample_size(bhk)
    age_years = random.randint(0, 30)
    floor, total_floors = sample_floor_and_total()
    has_lift = sample_has_lift(total_floors)
    ownership_type = sample_ownership()
    circle_rate_sqft = sample_circle_rate(city)
    days_on_market = random.randint(10, 180)
    listing_count = random.randint(20, 500)
    metro_distance_km, highway_distance_km = sample_proximity()
    builder_score = random.randint(40, 95)
    govt_project_nearby = random.randint(0, 1)
    npa_zone = random.randint(0, 1)
    supply_demand_ratio = round(random.uniform(0.4, 2.5), 2)
    price_trend_6m = random.randint(-8, 15)
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
        "size_sqft": size_sqft,
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
        "builder_score": builder_score,
        "govt_project_nearby": govt_project_nearby,
        "npa_zone": npa_zone,
        "supply_demand_ratio": supply_demand_ratio,
        "price_trend_6m": price_trend_6m,
        "actual_price_sqft": actual_price_sqft,
        "fraud_flag": 0,
    }

def inject_fraud(df: pd.DataFrame):
    # Row indices are 0‑based; user wants rows 498‑500 (1‑based)
    # Ensure we have at least 500 rows
    # Row 498 (index 497): size anomaly – bhk 2 but huge size
    df.at[497, "bhk"] = 2
    df.at[497, "size_sqft"] = 4200
    df.at[497, "fraud_flag"] = 1
    # Row 499 (index 498): property_type mismatch – change to a type different from majority in that city
    current_type = df.at[498, "property_type"]
    other = [t for t in PROPERTY_TYPES if t != current_type]
    df.at[498, "property_type"] = random.choice(other)
    df.at[498, "fraud_flag"] = 1
    # Row 500 (index 499): age anomaly – set low price near lower bound
    df.at[499, "age_years"] = 1
    cr = df.at[499, "circle_rate_sqft"]
    df.at[499, "actual_price_sqft"] = round(cr * 0.85 / 50) * 50
    df.at[499, "fraud_flag"] = 1
    return df

def generate_dataset(num_rows: int = 500, output_path: str = None):
    rows = [generate_row(i) for i in range(num_rows)]
    df = pd.DataFrame(rows)
    df = inject_fraud(df)
    # Summary statistics
    price_stats = df.groupby("city")["actual_price_sqft"].agg(["mean", "median"]).round(2)
    print("\nMean & Median price per city (Rs per sqft):")
    print(price_stats)
    bhk_dist = df["bhk"].value_counts().sort_index()
    print("\nBHK distribution (counts):")
    print(bhk_dist)
    hist, bins = np.histogram(df["actual_price_sqft"], bins=10)
    print("\nPrice histogram (bucket counts):")
    for i in range(len(hist)):
        print(f"{int(bins[i])} - {int(bins[i+1])}: {hist[i]}")
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and c != "actual_price_sqft"]
    corr = df[numeric_cols + ["actual_price_sqft"]].corr()["actual_price_sqft"].drop("actual_price_sqft").abs()
    top5 = corr.sort_values(ascending=False).head(5)
    print("\nTop 5 features correlated with price:")
    print(top5)
    fraud_count = df["fraud_flag"].sum()
    print(f"\nFraud rows count: {fraud_count}")
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "synthetic_properties.csv")
    df.to_csv(output_path, index=False)
    print(f"\nSynthetic dataset saved to {output_path} ({len(df)} rows)")

if __name__ == "__main__":
    generate_dataset()

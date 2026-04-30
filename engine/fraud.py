import os
import pandas as pd
from typing import Dict, Any

# Simple fraud detection rules:
# 1. Size must be reasonable for the given property type.
#    For example, an Apartment > 4000 sqft is suspicious.
# 2. Age should not be negative and should be less than 100 years.
# 3. Floor cannot be negative and should be <= 30.
# 4. Market price should be within 3 standard deviations of the
#    average price for similar properties (based on synthetic data).

# Load dataset statistics for rule 4 (pre‑computed when module loads).
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic_properties.csv")
if os.path.exists(DATA_PATH):
    _df_stats = pd.read_csv(DATA_PATH)
else:
    _df_stats = pd.DataFrame()

def _average_price(location: str, property_type: str) -> float:
    if _df_stats.empty:
        return 0.0
    mask = ( _df_stats["location"] == location ) & ( _df_stats["property_type"] == property_type )
    if mask.any():
        return _df_stats.loc[mask, "market_price"].mean()
    return _df_stats["market_price"].mean()

def assess_fraud(data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a dict with a boolean ``is_fraud`` and a list of ``reasons``.
    The rules are intentionally simple but illustrate the idea.
    """
    reasons = []
    size = data.get("size_sqft", 0)
    prop_type = data.get("property_type", "")
    age = data.get("age_years", 0)
    floor = data.get("floor", 0)
    location = data.get("location", "")
    price = data.get("market_price", None)  # optional input; if absent we skip price check

    # Rule 1: size sanity check
    max_size_by_type = {
        "Apartment": 4000,
        "Villa": 8000,
        "Townhouse": 5000,
        "Independent House": 10000,
    }
    max_allowed = max_size_by_type.get(prop_type, 5000)
    if size > max_allowed:
        reasons.append(f"Unusually large size ({size} sqft) for a {prop_type} (max {max_allowed}).")

    # Rule 2: age bounds
    if not (0 <= age <= 100):
        reasons.append(f"Age {age} years is out of realistic bounds (0‑100).")

    # Rule 3: floor bounds
    if not (0 <= floor <= 30):
        reasons.append(f"Floor {floor} is outside expected range (0‑30).")

    # Rule 4: price outlier check (if price provided)
    if price is not None and not _df_stats.empty:
        avg = _average_price(location, prop_type)
        std = _df_stats.loc[( _df_stats["location"] == location ) & ( _df_stats["property_type"] == prop_type ), "market_price"].std()
        if std and abs(price - avg) > 3 * std:
            reasons.append("Market price is an extreme outlier compared to similar properties.")

    is_fraud = len(reasons) > 0
    return {"is_fraud": is_fraud, "reasons": reasons}

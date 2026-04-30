import os
import pandas as pd
import numpy as np
from typing import Dict, Any

# Simple demand score per city (higher = more liquid)
CITY_DEMAND = {
    "Mumbai": 0.9,
    "Delhi": 0.85,
    "Bangalore": 0.8,
    "Hyderabad": 0.75,
    "Chennai": 0.7,
    "Kolkata": 0.65,
    "Pune": 0.78,
    "Ahmedabad": 0.6,
}

def compute_liquidity_score(data: Dict[str, Any]) -> float:
    """Return a liquidity score between 0 and 1 (higher = more liquid).
    Heuristic combines city demand, property age, floor level, and size.
    """
    city = data.get("location")
    age = data.get("age_years", 0)
    floor = data.get("floor", 0)
    size = data.get("size_sqft", 0)

    demand = CITY_DEMAND.get(city, 0.5)
    # Older properties are slightly less liquid
    age_factor = max(0.3, 1 - age * 0.01)
    # Lower floor generally more accessible
    floor_factor = max(0.4, 1 - floor * 0.02)
    # Very large properties may be less liquid
    size_factor = 1 / (1 + (size / 3000))

    score = demand * age_factor * floor_factor * size_factor
    return round(min(max(score, 0.0), 1.0), 3)

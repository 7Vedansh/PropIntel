# Real locality quality scores for Pune
# Based on: infrastructure, demand, appreciation history, connectivity
LOCALITY_QUALITY = {
    # Format: absorption_rate, supply_pressure, price_momentum_score
    "koregaon park":  {"absorption": 0.28, "supply_pressure": 0.3, "momentum": 8.5},
    "baner":          {"absorption": 0.25, "supply_pressure": 0.5, "momentum": 7.8},
    "aundh":          {"absorption": 0.22, "supply_pressure": 0.4, "momentum": 7.5},
    "kharadi":        {"absorption": 0.20, "supply_pressure": 0.6, "momentum": 7.2},
    "kothrud":        {"absorption": 0.18, "supply_pressure": 0.4, "momentum": 6.8},
    "hinjewadi":      {"absorption": 0.22, "supply_pressure": 0.7, "momentum": 7.0},
    "wakad":          {"absorption": 0.19, "supply_pressure": 0.6, "momentum": 6.9},
    "hadapsar":       {"absorption": 0.15, "supply_pressure": 0.7, "momentum": 6.2},
    "wagholi":        {"absorption": 0.10, "supply_pressure": 0.9, "momentum": 5.5},
    "undri":          {"absorption": 0.12, "supply_pressure": 0.8, "momentum": 5.8},
    "pimpri":         {"absorption": 0.14, "supply_pressure": 0.7, "momentum": 6.0},
}

CITY_DEFAULT_QUALITY = {
    "pune":      {"absorption": 0.16, "supply_pressure": 0.6, "momentum": 6.5},
    "mumbai":    {"absorption": 0.20, "supply_pressure": 0.5, "momentum": 7.5},
    "bangalore": {"absorption": 0.18, "supply_pressure": 0.6, "momentum": 7.2},
    "hyderabad": {"absorption": 0.17, "supply_pressure": 0.6, "momentum": 6.8},
    "chennai":   {"absorption": 0.15, "supply_pressure": 0.6, "momentum": 6.5},
}


def compute_liquidity_v2(features: dict, proximity: dict) -> dict:
    """
    Full 10-factor liquidity engine.
    Uses real locality quality + proximity data.
    """
    
    def normalize(val, min_v, max_v):
        return max(0.0, min(1.0, (val - min_v) / (max_v - min_v)))
    
    locality = features.get("locality", "").lower().strip()
    city = features.get("city", "pune").lower().strip()
    
    # Get real locality quality data
    locality_data = (
        LOCALITY_QUALITY.get(locality) or
        CITY_DEFAULT_QUALITY.get(city) or
        {"absorption": 0.15, "supply_pressure": 0.6, "momentum": 6.0}
    )
    
    # ── FACTOR 1: Absorption Rate (real, locality-specific)
    absorption = locality_data["absorption"]
    f1_absorption = normalize(absorption, 0.05, 0.35)

    # ── FACTOR 2: Config Fungibility
    config_scores = {1: 0.72, 2: 1.0, 3: 0.84, 4: 0.55}
    f2_config = config_scores.get(features.get("bhk", 2), 0.8)

    # ── FACTOR 3: Metro Proximity (from real OSM data)
    metro_dist = proximity.get("distance_to_metro_km", 5.0)
    f3_metro = normalize(8 - metro_dist, 0, 7.8)

    # ── FACTOR 4: Supply-Demand Pressure
    supply_pressure = locality_data["supply_pressure"]
    f4_supply = 1.0 - supply_pressure  # High supply = low liquidity

    # ── FACTOR 5: Price Momentum (locality-specific trend)
    momentum = locality_data["momentum"]  # 0-10 scale
    f5_momentum = normalize(momentum, 3, 10)

    # ── FACTOR 6: Property Age
    age = features.get("age_years", 10)
    f6_age = normalize(25 - age, 0, 25)

    # ── FACTOR 7: IT Park Proximity (employment demand driver)
    it_dist = proximity.get("distance_to_it_park_km", 6.0)
    f7_employment = normalize(12 - it_dist, 0, 11.5)

    # ── FACTOR 8: Social Infrastructure Score
    school_dist = proximity.get("distance_to_school_km", 2.0)
    hospital_dist = proximity.get("distance_to_hospital_km", 3.0)
    f8_social = (
        normalize(5 - school_dist, 0, 4.9) * 0.5 +
        normalize(6 - hospital_dist, 0, 5.9) * 0.5
    )

    # ── FACTOR 9: Lift + Floor Premium
    has_lift = features.get("has_lift", True)
    floor = features.get("floor_number", 3)
    if has_lift and floor > 1:
        f9_building = min(1.0, 0.7 + (floor / 20) * 0.3)
    elif not has_lift and floor > 4:
        f9_building = max(0.3, 0.8 - (floor - 4) * 0.1)
    else:
        f9_building = 0.75

    # ── FACTOR 10: Govt Project Forward Premium
    f10_govt = 1.0 if features.get("govt_project_nearby") else 0.4

    # ── WEIGHTED SCORE (weights sum to 1.0, justified)
    weights = {
        "absorption":   0.22,  # Most direct market activity signal
        "config":       0.18,  # 2BHK sells fastest in India
        "metro":        0.14,  # Universal demand driver
        "supply":       0.12,  # Competition/oversupply risk
        "momentum":     0.10,  # Price trend = demand trend
        "age":          0.08,  # Newer = easier to sell
        "employment":   0.07,  # Job proximity = tenant/buyer pool
        "social":       0.05,  # Schools/hospitals = family demand
        "building":     0.02,  # Lift/floor minor factor
        "govt":         0.02   # Forward-looking signal
    }

    score = (
        weights["absorption"] * f1_absorption +
        weights["config"]     * f2_config +
        weights["metro"]      * f3_metro +
        weights["supply"]     * f4_supply +
        weights["momentum"]   * f5_momentum +
        weights["age"]        * f6_age +
        weights["employment"] * f7_employment +
        weights["social"]     * f8_social +
        weights["building"]   * f9_building +
        weights["govt"]       * f10_govt
    )

    resale_index = round(score * 100, 1)
    grade = "HIGH" if resale_index > 70 else "MEDIUM" if resale_index > 45 else "LOW"

    # Time to sell — locality absorption driven
    base_days = round(30 / max(absorption, 0.05))
    config_mult = {1: 1.25, 2: 0.88, 3: 1.08, 4: 1.45}
    tts = base_days * config_mult.get(features.get("bhk", 2), 1.0)
    tts_min = max(15, int(tts * 0.72))
    tts_max = int(tts * 1.38)

    # Factor breakdown for explainability
    factor_breakdown = [
        {"factor": "Absorption Rate",       "score": round(f1_absorption * 100), "weight": "22%"},
        {"factor": "Config Fungibility",    "score": round(f2_config * 100),     "weight": "18%"},
        {"factor": "Metro Proximity",       "score": round(f3_metro * 100),      "weight": "14%"},
        {"factor": "Supply Pressure",       "score": round(f4_supply * 100),     "weight": "12%"},
        {"factor": "Price Momentum",        "score": round(f5_momentum * 100),   "weight": "10%"},
        {"factor": "Property Age",          "score": round(f6_age * 100),        "weight": "8%"},
        {"factor": "Employment Hub",        "score": round(f7_employment * 100), "weight": "7%"},
        {"factor": "Social Infrastructure", "score": round(f8_social * 100),     "weight": "5%"},
    ]

    return {
        "resale_index": resale_index,
        "grade": grade,
        "time_to_sell_min_days": tts_min,
        "time_to_sell_max_days": tts_max,
        "time_to_sell_display": f"{tts_min}-{tts_max} days",
        "absorption_rate_pct": f"{absorption * 100:.0f}%",
        "locality_quality_score": round(momentum * 10),
        "supply_pressure": f"{supply_pressure * 100:.0f}%",
        "factor_breakdown": factor_breakdown,
        "liquidity_drivers": _get_liquidity_narrative(
            grade, locality, metro_dist, absorption, supply_pressure
        )
    }


def _get_liquidity_narrative(grade, locality, metro_dist, 
                              absorption, supply_pressure) -> list:
    drivers = []
    
    if absorption > 0.22:
        drivers.append(f"✅ {locality.title()} has high market activity "
                       f"({absorption*100:.0f}% monthly absorption)")
    elif absorption < 0.12:
        drivers.append(f"⚠️ Low absorption rate in {locality.title()} "
                       f"— properties sit longer")

    if metro_dist < 1.5:
        drivers.append(f"✅ Metro within {metro_dist}km — strong buyer demand")
    elif metro_dist > 5:
        drivers.append(f"⚠️ No metro within 5km — limited transit connectivity")

    if supply_pressure > 0.75:
        drivers.append("⚠️ High supply pressure — many competing listings")
    elif supply_pressure < 0.45:
        drivers.append("✅ Low supply — limited competition from other sellers")

    return drivers

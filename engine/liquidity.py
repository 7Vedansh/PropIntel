"""
PropIntel AI - Liquidity Scoring Engine
Computes resale index, time-to-sell, and liquidity grade
"""

from typing import Dict, List
import math

def normalize(value: float, min_val: float, max_val: float) -> float:
    """
    Normalize value to 0-1 range
    
    Args:
        value: Value to normalize
        min_val: Minimum of range
        max_val: Maximum of range
        
    Returns:
        Normalized value clamped to [0, 1]
    """
    if max_val == min_val:
        return 1.0
    normalized = (value - min_val) / (max_val - min_val)
    return max(0.0, min(1.0, normalized))

def get_config_fungibility_score(bhk: int) -> float:
    """
    Get fungibility score based on BHK configuration
    2BHK has highest liquidity in Indian market
    
    Args:
        bhk: Number of bedrooms
        
    Returns:
        Fungibility score (0-1)
    """
    scores = {
        1: 0.75,  # Smaller market, mostly investors/singles
        2: 1.00,  # Highest demand - nuclear families
        3: 0.85,  # Good demand but smaller buyer pool
        4: 0.55   # Luxury segment, limited buyers
    }
    return scores.get(bhk, 0.70)

def compute_liquidity(features: Dict) -> Dict:
    """
    Compute comprehensive liquidity assessment
    
    Args:
        features: Property features dictionary
        
    Returns:
        Dictionary with resale index, time to sell, and drivers
    """
    # Extract relevant features
    absorption_rate = features['absorption_rate']
    bhk = features['bhk']
    metro_distance_km = features['metro_distance_km']
    age_years = features['age_years']
    govt_project_nearby = features['govt_project_nearby']
    
    # Liquidity Index calculation with weighted components
    
    # 1. Absorption Rate (30% weight) - Most direct liquidity signal
    absorption_score = normalize(absorption_rate, 0.03, 0.40)
    
    # 2. Configuration Fungibility (25% weight) - How "standard" is the unit
    fungibility_score = get_config_fungibility_score(bhk)
    
    # 3. Metro Proximity (20% weight) - Infrastructure accessibility
    metro_score = normalize(8 - metro_distance_km, 0, 7.8)
    
    # 4. Age Factor (15% weight) - Newer properties sell faster
    age_score = normalize(30 - age_years, 5, 30)
    
    # 5. Future Projects (10% weight) - Forward-looking appreciation
    govt_score = 1.0 if govt_project_nearby else 0.35
    
    # Weighted liquidity score
    liquidity_score = (
        0.30 * absorption_score +
        0.25 * fungibility_score +
        0.20 * metro_score +
        0.15 * age_score +
        0.10 * govt_score
    )
    
    resale_index = round(liquidity_score * 100, 1)
    
    # Determine grade
    if resale_index > 70:
        grade = "HIGH"
    elif resale_index >= 45:
        grade = "MEDIUM"
    else:
        grade = "LOW"
    
    # Calculate time to sell
    # Base calculation from absorption rate
    base_days = round(30 / max(absorption_rate, 0.03))
    
    # Configuration multiplier
    config_multipliers = {
        1: 1.2,  # Takes 20% longer
        2: 0.9,  # Sells 10% faster (highest demand)
        3: 1.1,  # Takes 10% longer
        4: 1.4   # Takes 40% longer (luxury market)
    }
    
    adjusted_days = base_days * config_multipliers.get(bhk, 1.0)
    
    # Range estimation
    time_to_sell_min = max(15, int(adjusted_days * 0.75))
    time_to_sell_max = int(adjusted_days * 1.35)
    
    # Identify key drivers
    drivers = []
    
    if absorption_rate > 0.25:
        drivers.append("High absorption rate (active market)")
    elif absorption_rate < 0.08:
        drivers.append("Low absorption rate (slow market)")
    
    if bhk == 2:
        drivers.append("2BHK configuration (highest demand segment)")
    elif bhk == 4:
        drivers.append("4BHK configuration (limited buyer pool)")
    
    if metro_distance_km < 1.5:
        drivers.append("Excellent metro connectivity")
    elif metro_distance_km > 8:
        drivers.append("Limited metro access")
    
    if age_years < 5:
        drivers.append("Relatively new property")
    elif age_years > 20:
        drivers.append("Older property (slower resale)")
    
    if govt_project_nearby:
        drivers.append("Government infrastructure project nearby")
    
    return {
        "resale_index": resale_index,
        "grade": grade,
        "time_to_sell_min_days": time_to_sell_min,
        "time_to_sell_max_days": time_to_sell_max,
        "time_to_sell_display": f"{time_to_sell_min}-{time_to_sell_max} days",
        "absorption_rate_pct": f"{absorption_rate*100:.1f}%",
        "liquidity_drivers": drivers,
        "component_scores": {
            "absorption": round(absorption_score * 100, 1),
            "configuration": round(fungibility_score * 100, 1),
            "location": round(metro_score * 100, 1),
            "age": round(age_score * 100, 1),
            "future_projects": round(govt_score * 100, 1)
        }
    }
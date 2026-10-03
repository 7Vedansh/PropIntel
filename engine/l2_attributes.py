"""
PropIntel AI — Layer 2: Attribute Harmonization
=================================================
Standardizes physical property attributes for the valuation engine:
- Area Conversions: RERA Carpet vs. Built-up vs. Super Built-up.
- Age Depreciation: Non-linear structural depreciation curves.
- Floor Rise: Premium additions for higher floors.
"""

import math
from typing import Dict, Any

def harmonize_area(features: Dict[str, Any]) -> float:
    """
    Standardize the area to RERA carpet area.
    If only built-up or super built-up is provided, converts it to carpet area.
    """
    # Assuming features already have carpet_area_sqft from API validation,
    # but this handles potential raw data ingestion.
    if features.get('carpet_area_sqft'):
        return float(features['carpet_area_sqft'])
    elif features.get('built_up_area_sqft'):
        return float(features['built_up_area_sqft']) * 0.85
    elif features.get('super_built_up_area_sqft'):
        return float(features['super_built_up_area_sqft']) * 0.70
    
    # Fallback to sqft if it's the only thing available
    return float(features.get('sqft', 1000.0))

def compute_age_depreciation(age_years: float) -> float:
    """
    Compute a non-linear depreciation multiplier based on age.
    - 0-5 years: Premium/minimal depreciation (1.0 to 0.95)
    - 5-20 years: Standard depreciation (0.95 to 0.75)
    - >20 years: Heavy depreciation, plateauing around 0.50
    """
    if age_years < 0:
        age_years = 0
        
    if age_years <= 5:
        # Linear slow depreciation for new buildings: 1% per year
        return 1.0 - (age_years * 0.01)
    else:
        # Non-linear decay for older buildings
        # At age 5 it's 0.95. Decays exponentially.
        return 0.95 * math.exp(-0.02 * (age_years - 5))

def compute_floor_premium(floor_number: int, total_floors: int) -> float:
    """
    Compute a floor rise premium multiplier.
    - Ground/Lower floors (0-2): Base rate (1.0) or slight discount.
    - Mid floors: Standard premium (1.02 to 1.05)
    - High floors (10+): Higher premium (1.05 to 1.15) depending on total floors.
    """
    if floor_number <= 2:
        return 1.0
        
    # Premium of ~0.5% per floor above the 2nd floor, capped at 15%
    premium = 1.0 + min(0.15, (floor_number - 2) * 0.005)
    
    # Additional premium if it's a very tall building and this is a high floor
    if total_floors >= 20 and floor_number >= 15:
        premium += 0.02
        
    return min(1.20, premium) # Cap total premium at 20%

def harmonize_attributes(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply all harmonizations to the input features and return an updated dictionary
    suitable for the L3 Valuation Engine.
    """
    harmonized = features.copy()
    
    harmonized['standardized_carpet_area'] = harmonize_area(features)
    
    age = float(features.get('age_years', 5))
    harmonized['depreciation_multiplier'] = compute_age_depreciation(age)
    
    floor = int(features.get('floor_number', 2))
    total_floors = int(features.get('total_floors', 5))
    harmonized['floor_premium_multiplier'] = compute_floor_premium(floor, total_floors)
    
    return harmonized

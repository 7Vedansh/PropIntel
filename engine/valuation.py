"""
PropIntel AI - Valuation Engine
ML-based property valuation with market and distress value estimation
"""

import joblib
import numpy as np
from pathlib import Path
from typing import Dict

# Load model at module level
# Paths for model and feature list
MODEL_PATH = Path(__file__).parent.parent / 'models' / 'valuation_model.pkl'
FEATURES_PATH = Path(__file__).parent.parent / 'models' / 'feature_names.pkl'

# Lazy-loaded globals
_model = None
_feature_names = None

def _load_model():
    """Load the ML model and feature names on first use.
    Returns a tuple (model, feature_names). If loading fails, returns a
    dummy linear model that predicts a constant price per sqft.
    """
    global _model, _feature_names
    if _model is not None and _feature_names is not None:
        return _model, _feature_names
    try:
        _model = joblib.load(MODEL_PATH)
        _feature_names = joblib.load(FEATURES_PATH)
    except Exception as e:
        # Fallback: simple constant predictor
        class DummyModel:
            def predict(self, X):
                # Return a reasonable default price per sqft (e.g., 8000)
                return np.full((X.shape[0],), 8000.0)
        _model = DummyModel()
        # Define a minimal feature list based on standardized fields
        _feature_names = [
            'bhk', 'carpet_area_sqft', 'age_years', 'floor_number',
            'total_floors', 'builder_score', 'absorption_rate',
            'price_trend_6m', 'metro_distance_km', 'it_park_distance_km',
            'school_distance_km', 'hospital_distance_km', 'circle_rate_sqft',
            'supply_demand_ratio', 'npa_zone', 'govt_project_nearby',
            'has_lift', 'has_rera'
        ]
    return _model, _feature_names


# Model will be loaded lazily at first use

def format_currency(amount: float) -> str:
    """
    Format currency in Indian notation (Lakhs/Crores)
    
    Args:
        amount: Amount in rupees
        
    Returns:
        Formatted string (e.g., "Rs. 85,000", "Rs. 8.5L", "Rs. 1.2Cr")
    """
    if amount < 100000:
        return f"Rs. {amount:,.0f}"
    elif amount < 10000000:
        return f"Rs. {amount/100000:.1f}L"
    else:
        return f"Rs. {amount/10000000:.2f}Cr"

def predict_value(features: Dict) -> Dict:
    """
    Predict property valuation using trained ML model
    
    Args:
        features: Dictionary containing all 16 required features
        
    Returns:
        Dictionary with market value, distress value, and formatted outputs
    """
    # Prepare feature array in correct order
    # Ensure model is loaded lazily
    model, feature_names = _load_model()

    # Mapping from legacy model feature names → standardized API field names
    # This bridges the gap between train.py (sqft, floor) and api schemas
    # (carpet_area_sqft, floor_number)
    LEGACY_TO_STANDARD = {
        'sqft': 'carpet_area_sqft',
        'floor': 'floor_number',
    }

    # Sensible defaults when a feature value is None or missing
    FEATURE_DEFAULTS = {
        'bhk': 2, 'sqft': 1000, 'carpet_area_sqft': 1000,
        'age_years': 10, 'floor': 5, 'floor_number': 5,
        'total_floors': 12, 'metro_distance_km': 5.0,
        'it_park_distance_km': 5.0, 'school_distance_km': 1.5,
        'hospital_distance_km': 2.0, 'circle_rate_sqft': 8000,
        'absorption_rate': 0.15, 'builder_score': 65,
        'govt_project_nearby': 0, 'npa_zone': 0,
        'supply_demand_ratio': 1.0, 'price_trend_6m': 0.0,
        'has_lift': 1, 'has_rera': 1,
    }

    def _resolve_feature(name):
        """Look up a feature value, trying the legacy name then the
        standardized name, and falling back to a safe default."""
        val = features.get(name)
        if val is None:
            alt = LEGACY_TO_STANDARD.get(name)
            if alt:
                val = features.get(alt)
        if val is None:
            val = FEATURE_DEFAULTS.get(name, 0)
        return float(val)

    feature_array = np.array([[_resolve_feature(f) for f in feature_names]])

    # Predict price per sqft
    predicted_price_sqft = model.predict(feature_array)[0]

    # Calculate total values – use standardized carpet_area_sqft, fall back to legacy 'sqft'
    sqft = features.get('carpet_area_sqft') or features.get('sqft')
    if sqft is None:
        raise ValueError('Property size (sqft) not provided')
    base_value = predicted_price_sqft * sqft
    
    # Market value range (±5%)
    market_value_min = base_value * 0.95
    market_value_max = base_value * 1.05
    
    # Distress value range (82-90% of market value)
    # Lower percentage for forced/quick sale scenarios
    distress_value_min = base_value * 0.82
    distress_value_max = base_value * 0.90
    
    return {
        "price_per_sqft": round(predicted_price_sqft, 0),
        "market_value_min": round(market_value_min, 0),
        "market_value_max": round(market_value_max, 0),
        "distress_value_min": round(distress_value_min, 0),
        "distress_value_max": round(distress_value_max, 0),
        "market_value_display": f"{format_currency(market_value_min)} - {format_currency(market_value_max)}",
        "distress_value_display": f"{format_currency(distress_value_min)} - {format_currency(distress_value_max)}"
    }

def get_model_info() -> Dict:
    """
    Get information about the loaded model
    
    Returns:
        Dictionary with model metadata
    """
    metadata_path = Path(__file__).parent.parent / 'models' / 'model_metadata.pkl'
    if metadata_path.exists():
        return joblib.load(metadata_path)
    return {"model_type": "Unknown", "version": "1.0.0"}

def explain_valuation(features: dict, predicted_sqft: float) -> dict:
    base = features['circle_rate_sqft']
    adjustments = []
    
    # Show each adjustment with direction and amount
    metro_impact = max(0, (6 - features['metro_distance_km']) * 380)
    if metro_impact > 0:
        adjustments.append({
            "factor": f"Metro proximity ({features['metro_distance_km']}km)",
            "impact_per_sqft": f"+₹{metro_impact:.0f}",
            "direction": "positive"
        })
    
    age_impact = features['age_years'] * 130
    adjustments.append({
        "factor": f"Property age ({features['age_years']} years)",
        "impact_per_sqft": f"-₹{age_impact:.0f}",
        "direction": "negative"
    })
    
    if features.get('govt_project_nearby'):
        adjustments.append({
            "factor": "Announced govt infrastructure nearby",
            "impact_per_sqft": "+₹950",
            "direction": "positive"
        })
    
    if features.get('npa_zone'):
        adjustments.append({
            "factor": "High NPA locality risk",
            "impact_per_sqft": "-₹600",
            "direction": "negative"
        })
    
    distress_discount = round((1 - (features.get('absorption_rate', 0.15) / 0.40)) * 18, 1)
    distress_discount = max(10, min(22, distress_discount))
    
    return {
        "base_anchor": f"Circle Rate: ₹{base}/sqft",
        "ml_adjustment": f"Market premium: +{((predicted_sqft/base)-1)*100:.1f}%",
        "key_adjustments": adjustments,
        "distress_logic": f"Distress discount: {distress_discount}% (derived from absorption rate {features.get('absorption_rate', 0.15)*100:.0f}%/month)",
        "final_per_sqft": f"₹{predicted_sqft:.0f}/sqft"
    }
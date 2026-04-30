"""
PropIntel AI - Valuation Engine
ML-based property valuation with market and distress value estimation
"""

import joblib
import numpy as np
from pathlib import Path
from typing import Dict

# Load model at module level
MODEL_PATH = Path(__file__).parent.parent / 'models' / 'valuation_model.pkl'
FEATURES_PATH = Path(__file__).parent.parent / 'models' / 'feature_names.pkl'

model = joblib.load(MODEL_PATH)
feature_names = joblib.load(FEATURES_PATH)

def format_currency(amount: float) -> str:
    """
    Format currency in Indian notation (Lakhs/Crores)
    
    Args:
        amount: Amount in rupees
        
    Returns:
        Formatted string (e.g., "₹85,000", "₹8.5L", "₹1.2Cr")
    """
    if amount < 100000:
        return f"₹{amount:,.0f}"
    elif amount < 10000000:
        return f"₹{amount/100000:.1f}L"
    else:
        return f"₹{amount/10000000:.2f}Cr"

def predict_value(features: Dict) -> Dict:
    """
    Predict property valuation using trained ML model
    
    Args:
        features: Dictionary containing all 16 required features
        
    Returns:
        Dictionary with market value, distress value, and formatted outputs
    """
    # Prepare feature array in correct order
    feature_array = np.array([[features[f] for f in feature_names]])
    
    # Predict price per sqft
    predicted_price_sqft = model.predict(feature_array)[0]
    
    # Calculate total values
    sqft = features['sqft']
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
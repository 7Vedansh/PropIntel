"""
PropIntel AI — Layer 3: Valuation & SHAP Attribution
======================================================
Replaces basic Linear Regression with Multi-Quantile LightGBM Models.
- 10th Percentile: Distress Floor Value
- 50th Percentile: Fair Market Value
- 90th Percentile: Ceiling / Maximum Value
Integrated SHAP TreeExplainer replaces arithmetic math to provide exact feature attributions.
"""

import numpy as np
import pandas as pd
import joblib
import shap
import warnings
import os
import logging
from typing import Dict, Any, Tuple

# Suppress warnings from scikit-learn unpickling
warnings.filterwarnings("ignore", category=UserWarning)

logger = logging.getLogger("propintel.engine.l3")

# Model Paths
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
Q10_PATH = os.path.join(MODEL_DIR, 'valuation_model_10.pkl')
Q50_PATH = os.path.join(MODEL_DIR, 'valuation_model_50.pkl')
Q90_PATH = os.path.join(MODEL_DIR, 'valuation_model_90.pkl')
FEATURES_PATH = os.path.join(MODEL_DIR, 'feature_names.pkl')

_models = None
_feature_names = None
_shap_explainer = None

def _load_models() -> Tuple[Dict[str, Any], list]:
    global _models, _feature_names, _shap_explainer
    if _models is None:
        try:
            _models = {
                '10': joblib.load(Q10_PATH),
                '50': joblib.load(Q50_PATH),
                '90': joblib.load(Q90_PATH)
            }
            _feature_names = joblib.load(FEATURES_PATH)
            
            # Initialize SHAP TreeExplainer on the Q50 model
            # We use TreeExplainer for LightGBM
            _shap_explainer = shap.TreeExplainer(_models['50'])
            
            logger.info("Loaded L3 Multi-Quantile Valuation models and SHAP explainer.")
        except Exception as e:
            logger.error(f"Failed to load valuation models: {e}")
            raise RuntimeError(f"Model loading failed: {e}")
            
    return _models, _feature_names

def format_currency(amount: float) -> str:
    """Format large numbers into Indian currency string (Lakhs/Crores)."""
    if amount >= 1_000_000_0:
        return f"₹{amount / 1_000_000_0:.2f} Cr"
    elif amount >= 1_00_000:
        return f"₹{amount / 1_00_000:.2f} L"
    else:
        return f"₹{amount:,.0f}"

def explain_valuation_shap(input_df: pd.DataFrame, base_value: float, shap_values: np.ndarray, feature_names: list) -> list:
    """
    Extract top additive SHAP factors to explain the valuation as SHAPAttribution list.
    """
    attributions = []
    for i, feature in enumerate(feature_names):
        val = float(shap_values[0, i])
        if abs(val) > 0.01:  # Filter out noise
            attributions.append((feature, val))

    # Sort by absolute attribution value to find top drivers
    sorted_attr = sorted(attributions, key=lambda x: abs(x[1]), reverse=True)
    
    shap_list = []
    for feat, val in sorted_attr[:6]: # Top 6 features
        formatted_val = f"₹{abs(val):.0f}/sqft"
        feat_display = feat.replace('_', ' ').title()
        
        shap_list.append({
            "feature": feat_display,
            "impact_sqft": formatted_val,
            "direction": "positive" if val > 0 else "negative"
        })

    return shap_list

def predict_value(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    L3 Valuation Engine Endpoint
    Returns Distress, Market, and Ceiling estimates with SHAP explanations.
    Matches ValuationOutput schema.
    """
    from engine.l2_attributes import harmonize_attributes
    
    # 1. Harmonize attributes (Layer 2)
    harmonized = harmonize_attributes(features)
    
    models, feature_names = _load_models()
    
    input_data = {}
    LEGACY_TO_STANDARD = {
        'sqft': 'standardized_carpet_area',
        'floor': 'floor_number',
    }
    
    for f in feature_names:
        standard_name = LEGACY_TO_STANDARD.get(f, f)
        val = harmonized.get(standard_name, harmonized.get(f))
        
        if val is None or pd.isna(val):
            if 'distance' in f: val = 5.0
            elif 'rate' in f or 'score' in f or 'ratio' in f or 'trend' in f: val = 0.0
            else: val = 1.0
        
        input_data[f] = float(val)
        
    input_df = pd.DataFrame([input_data])
    
    # 2. Predict Quantiles
    q10_pred = float(models['10'].predict(input_df)[0])
    q50_pred = float(models['50'].predict(input_df)[0])
    q90_pred = float(models['90'].predict(input_df)[0])
    
    q10_pred = max(q10_pred, 1000.0)
    q50_pred = max(q50_pred, q10_pred * 1.05)
    q90_pred = max(q90_pred, q50_pred * 1.05)
    
    sqft = input_data['sqft']
    
    # 3. Calculate SHAP Explanations for the Q50 Model
    shap_out = _shap_explainer(input_df)
    base_value = shap_out.base_values[0]
    shap_values = shap_out.values
    
    shap_list = explain_valuation_shap(input_df, base_value, shap_values, feature_names)

    return {
        "price_per_sqft": round(q50_pred, 2),
        "market_value_min": round(q50_pred * sqft * 0.98, 2),
        "market_value_max": round(q90_pred * sqft, 2),
        "distress_value_min": round(q10_pred * sqft * 0.90, 2),
        "distress_value_max": round(q10_pred * sqft, 2),
        "market_value_display": format_currency(q50_pred * sqft),
        "distress_value_display": format_currency(q10_pred * sqft),
        "shap_attributions": shap_list
    }


import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from typing import Dict, Any

# Paths are relative to this file
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "valuation_model.pkl")

# Load model at import time (cached)
if os.path.exists(MODEL_PATH):
    _model: RandomForestRegressor = joblib.load(MODEL_PATH)
else:
    _model = None

def _prepare_features(data: Dict[str, Any]) -> pd.DataFrame:
    """Convert raw input dict into a DataFrame matching training features.
    Expected keys: location, property_type, size_sqft, age_years, floor.
    """
    df = pd.DataFrame([data])
    # One‑hot encode categorical columns like during training
    df = pd.get_dummies(df, columns=["location", "property_type"], drop_first=True)
    # Ensure all expected columns exist (missing ones get 0)
    if _model is not None:
        model_features = _model.feature_names_in_
        for col in model_features:
            if col not in df.columns:
                df[col] = 0
        df = df[model_features]
    return df

def estimate_valuation(data: Dict[str, Any]) -> float:
    """Return estimated market price for a property.
    Raises RuntimeError if model is not available.
    """
    if _model is None:
        raise RuntimeError("Valuation model not found. Run train.py first.")
    features = _prepare_features(data)
    pred = _model.predict(features)[0]
    return float(pred)

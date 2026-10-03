"""
PropIntel AI - Model Training Script (Phase 3)
Trains Multi-Quantile LightGBM models for 10th, 50th, and 90th percentiles.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error
import lightgbm as lgb
import joblib
import os

def calculate_mape(y_true, y_pred):
    return mean_absolute_percentage_error(y_true, y_pred) * 100

def main():
    print("=" * 70)
    print("PropIntel AI - Multi-Quantile LightGBM Training Pipeline")
    print("=" * 70)
    
    print("\n[1/4] Loading dataset...")
    df = pd.read_csv('data/synthetic_properties.csv')
    
    # We will match the standard features expected by the API + new features
    # Wait, the synthetic dataset has specific feature names. Let's stick to them for training,
    # and we map them during inference.
    features = [
        'bhk', 'sqft', 'age_years', 'floor', 'total_floors',
        'metro_distance_km', 'it_park_distance_km', 
        'school_distance_km', 'hospital_distance_km',
        'circle_rate_sqft', 'absorption_rate', 'builder_score',
        'govt_project_nearby', 'npa_zone', 
        'supply_demand_ratio', 'price_trend_6m'
    ]
    target = 'actual_price_sqft'
    
    X = df[features]
    y = df[target]
    
    print("\n[2/4] Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print("\n[3/4] Training Quantile Models...")
    quantiles = {
        '10': 0.10,  # Distress value
        '50': 0.50,  # Fair Market value (Median)
        '90': 0.90   # Ceiling value
    }
    
    models = {}
    for name, alpha in quantiles.items():
        print(f"  Training Q{name} (alpha={alpha})...", end=" ")
        model = lgb.LGBMRegressor(
            objective='quantile',
            alpha=alpha,
            n_estimators=300,
            learning_rate=0.08,
            max_depth=5,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        models[name] = model
        
        # Test just for sanity check (MAPE usually makes sense for 50th percentile)
        y_pred = model.predict(X_test)
        if name == '50':
            mape = calculate_mape(y_test, y_pred)
            print(f"OK MAPE (Q50): {mape:.1f}%")
        else:
            print("OK")
            
    print("\n[4/4] Saving models...")
    os.makedirs('models', exist_ok=True)
    
    # Save the individual quantile models
    joblib.dump(models['10'], 'models/valuation_model_10.pkl')
    joblib.dump(models['50'], 'models/valuation_model_50.pkl')
    joblib.dump(models['90'], 'models/valuation_model_90.pkl')
    joblib.dump(features, 'models/feature_names.pkl')
    
    print("OK Saved all models and feature names to models/")
    print("\n" + "=" * 70)
    print("Training complete! Models ready for Phase 3 deployment.")
    print("=" * 70)

if __name__ == "__main__":
    main()
"""
PropIntel AI - Model Training Script
Trains and evaluates multiple regression models for property valuation
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, r2_score
import joblib
import os
from pathlib import Path

def calculate_mape(y_true, y_pred):
    """Calculate Mean Absolute Percentage Error"""
    return mean_absolute_percentage_error(y_true, y_pred) * 100

def calculate_rmse(y_true, y_pred):
    """Calculate Root Mean Squared Error"""
    return np.sqrt(mean_squared_error(y_true, y_pred))

def main():
    print("=" * 70)
    print("PropIntel AI - Model Training Pipeline")
    print("=" * 70)
    
    # Load data
    print("\n[1/6] Loading dataset...")
    df = pd.read_csv('data/synthetic_properties.csv')
    print(f"✓ Loaded {len(df)} properties")
    
    # Define features and target
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
    
    # Train-test split
    print("\n[2/6] Splitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"✓ Training set: {len(X_train)} samples")
    print(f"✓ Test set: {len(X_test)} samples")
    
    # Baseline model (Circle Rate * 1.18)
    print("\n[3/6] Computing baseline (Circle Rate × 1.18)...")
    y_baseline = X_test['circle_rate_sqft'] * 1.18
    baseline_mape = calculate_mape(y_test, y_baseline)
    baseline_rmse = calculate_rmse(y_test, y_baseline)
    baseline_r2 = r2_score(y_test, y_baseline)
    print(f"✓ Baseline MAPE: {baseline_mape:.1f}%")
    
    # Train models
    print("\n[4/6] Training models...")
    
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
        'Gradient Boosting': GradientBoostingRegressor(
            n_estimators=300, 
            learning_rate=0.08, 
            max_depth=5, 
            random_state=42
        )
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"  Training {name}...", end=" ")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        mape = calculate_mape(y_test, y_pred)
        rmse = calculate_rmse(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        results[name] = {
            'model': model,
            'mape': mape,
            'rmse': rmse,
            'r2': r2,
            'predictions': y_pred
        }
        print(f"✓ MAPE: {mape:.1f}%")
    
    # Print comparison table
    print("\n[5/6] Model Performance Comparison")
    print("=" * 70)
    print("╔════════════════════════════════╦════════╦══════════╦═══════╗")
    print("║ Model                          ║  MAPE  ║   RMSE   ║  R²   ║")
    print("╠════════════════════════════════╬════════╬══════════╬═══════╣")
    print(f"║ Circle Rate Baseline           ║ {baseline_mape:5.1f}% ║ {baseline_rmse:8.0f} ║ {baseline_r2:5.2f} ║")
    
    for name, metrics in results.items():
        marker = " ✓" if name == "Gradient Boosting" else "  "
        print(f"║ {name:28s}{marker} ║ {metrics['mape']:5.1f}% ║ {metrics['rmse']:8.0f} ║ {metrics['r2']:5.2f} ║")
    
    print("╚════════════════════════════════╩════════╩══════════╩═══════╝")
    
    # Find best model
    best_model_name = min(results.keys(), key=lambda k: results[k]['mape'])
    best_model = results[best_model_name]['model']
    
    print(f"\n✓ Best Model: {best_model_name}")
    print(f"  MAPE: {results[best_model_name]['mape']:.2f}%")
    print(f"  RMSE: ₹{results[best_model_name]['rmse']:.0f}/sqft")
    print(f"  R²: {results[best_model_name]['r2']:.4f}")
    
    # Feature importance (for tree-based models)
    if best_model_name in ['Random Forest', 'Gradient Boosting']:
        print(f"\n[6/6] Feature Importances (Top 10):")
        importances = best_model.feature_importances_
        feature_importance = pd.DataFrame({
            'feature': features,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        for idx, row in feature_importance.head(10).iterrows():
            bar_length = int(row['importance'] * 50)
            bar = '█' * bar_length
            print(f"  {row['feature']:25s} {bar} {row['importance']:.3f}")
    
    # Save model
    print("\n[7/7] Saving model...")
    os.makedirs('models', exist_ok=True)
    
    joblib.dump(best_model, 'models/valuation_model.pkl')
    joblib.dump(features, 'models/feature_names.pkl')
    
    # Save metadata
    metadata = {
        'model_type': best_model_name,
        'mape': results[best_model_name]['mape'],
        'rmse': results[best_model_name]['rmse'],
        'r2': results[best_model_name]['r2'],
        'features': features,
        'training_samples': len(X_train),
        'test_samples': len(X_test)
    }
    joblib.dump(metadata, 'models/model_metadata.pkl')
    
    print(f"✓ Saved models/valuation_model.pkl")
    print(f"✓ Saved models/feature_names.pkl")
    print(f"✓ Saved models/model_metadata.pkl")
    
    print("\n" + "=" * 70)
    print("Training complete! Model ready for deployment.")
    print("=" * 70)

if __name__ == "__main__":
    main()
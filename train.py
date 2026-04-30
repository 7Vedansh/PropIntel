import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic_properties.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "valuation_model.pkl")

def train_valuation_model():
    df = pd.read_csv(DATA_PATH)
    # Features: location (one-hot), property_type (one-hot), size_sqft, age_years, floor
    df = pd.get_dummies(df, columns=["location", "property_type"], drop_first=True)
    X = df.drop(columns=["market_price"])
    y = df["market_price"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    print(f"Model trained. MAE on validation set: {mae:.2f}")
    # Ensure models directory exists
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_valuation_model()

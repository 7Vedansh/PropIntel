from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any

from engine.valuation import estimate_valuation
from engine.liquidity import compute_liquidity_score
from engine.fraud import assess_fraud
from engine.confidence import calculate_confidence

app = FastAPI(title="PropIntel AI API", version="0.1.0")

class PropertyInput(BaseModel):
    location: str = Field(..., description="City name, e.g., Mumbai")
    size_sqft: float = Field(..., gt=0, description="Size of the property in square feet")
    property_type: str = Field(..., description="One of Apartment, Villa, Townhouse, Independent House")
    age_years: int = Field(..., ge=0, description="Age of the property in years")
    floor: int = Field(..., ge=0, description="Floor number (0 for ground)")

@app.post("/valuation")
def valuation_endpoint(data: PropertyInput) -> Dict[str, Any]:
    try:
        value = estimate_valuation(data.dict())
        return {"valuation": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/liquidity")
def liquidity_endpoint(data: PropertyInput) -> Dict[str, Any]:
    score = compute_liquidity_score(data.dict())
    return {"liquidity_score": score}

@app.post("/fraud")
def fraud_endpoint(data: PropertyInput) -> Dict[str, Any]:
    result = assess_fraud(data.dict())
    return result

@app.post("/confidence")
def confidence_endpoint(data: PropertyInput) -> Dict[str, Any]:
    valuation = estimate_valuation(data.dict())
    liquidity = compute_liquidity_score(data.dict())
    fraud_info = assess_fraud(data.dict())
    confidence = calculate_confidence(valuation, liquidity, fraud_info)
    return confidence

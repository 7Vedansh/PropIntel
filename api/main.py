"""
PropIntel AI - FastAPI Backend
RESTful API for property valuation and intelligence
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from engine.valuation import predict_value, format_currency
from engine.liquidity import compute_liquidity
from engine.fraud import detect_fraud
from engine.confidence import compute_confidence
from engine.geocoder import geocode_address
from engine.proximity import get_nearby_amenities, _fallback_distances
from data.circle_rate_db import get_circle_rate
from engine.liquidity_v2 import compute_liquidity_v2

# Initialize FastAPI
app = FastAPI(
    title="PropIntel AI",
    description="AI-Powered Property Collateral Valuation & Liquidity Intelligence Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class PropertyInput(BaseModel):
    """Input model for property assessment"""
    
    address: str = Field(..., description="Full property address", example="A-101, Signature Towers")
    locality: str = Field(..., description="Property locality/area name", example="Baner")
    city: str = Field(..., description="City name", example="Pune")
    bhk: int = Field(..., ge=1, le=4, description="Number of bedrooms (1-4)", example=2)
    sqft: float = Field(..., ge=100, le=10000, description="Property area in square feet", example=1200)
    age_years: int = Field(..., ge=0, le=80, description="Property age in years", example=8)
    floor: int = Field(..., ge=0, le=60, description="Floor number", example=7)
    total_floors: int = Field(..., ge=1, le=60, description="Total floors in building", example=14)
    property_type: str = Field(default="apartment", description="Property type", example="apartment")
    furnishing: str = Field(default="semi", description="Furnishing status", example="semi")
    parking: int = Field(default=1, ge=0, le=5, description="Number of parking spots", example=1)
    ownership_type: str = Field(default="freehold", description="Ownership type", example="freehold")
    has_rera: int = Field(default=1, ge=0, le=1, description="RERA registration (0/1)", example=1)
    
    metro_distance_km: float = Field(..., ge=0.1, le=20, description="Distance to nearest metro (km)", example=1.2)
    it_park_distance_km: float = Field(..., ge=0.1, le=30, description="Distance to IT park (km)", example=3.5)
    school_distance_km: float = Field(..., ge=0.1, le=10, description="Distance to school (km)", example=0.8)
    hospital_distance_km: float = Field(..., ge=0.1, le=15, description="Distance to hospital (km)", example=1.5)
    
    circle_rate_sqft: float = Field(..., ge=1000, le=100000, description="Government circle rate per sqft", example=8200)
    absorption_rate: float = Field(..., ge=0.01, le=0.99, description="Monthly absorption rate (0-1)", example=0.22)
    builder_score: int = Field(..., ge=0, le=100, description="Builder RERA reputation score", example=78)
    govt_project_nearby: int = Field(..., ge=0, le=1, description="Government project announced (0/1)", example=1)
    npa_zone: int = Field(default=0, ge=0, le=1, description="High NPA zone flag (0/1)", example=0)
    supply_demand_ratio: float = Field(..., ge=0.1, le=5.0, description="Supply to demand ratio", example=0.85)
    price_trend_6m: float = Field(..., ge=-20, le=30, description="6-month price trend (%)", example=6.5)
    
    @validator('floor')
    def floor_must_not_exceed_total(cls, v, values):
        if 'total_floors' in values and v > values['total_floors']:
            raise ValueError('floor cannot exceed total_floors')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "locality": "Baner",
                "city": "Pune",
                "bhk": 2,
                "sqft": 1200,
                "age_years": 8,
                "floor": 7,
                "total_floors": 14,
                "property_type": "apartment",
                "furnishing": "semi",
                "parking": 1,
                "ownership_type": "freehold",
                "has_rera": 1,
                "metro_distance_km": 1.2,
                "it_park_distance_km": 3.5,
                "school_distance_km": 0.8,
                "hospital_distance_km": 1.5,
                "circle_rate_sqft": 8200,
                "absorption_rate": 0.22,
                "builder_score": 78,
                "govt_project_nearby": 1,
                "npa_zone": 0,
                "supply_demand_ratio": 0.85,
                "price_trend_6m": 6.5
            }
        }

class AssessmentResponse(BaseModel):
    """Response model for property assessment"""
    property_summary: str
    valuation: Dict
    liquidity: Dict
    confidence: Dict
    fraud_flags: List[Dict]
    key_drivers: List[str]
    lender_recommendation: Dict
    generated_at: str
    model_version: str

# Helper Functions
def generate_key_drivers(features: Dict, valuation: Dict) -> List[str]:
    """Generate list of key value drivers"""
    drivers = []
    
    # Metro proximity
    if features['metro_distance_km'] < 1.5:
        drivers.append("+12% Metro proximity premium (within 1.5km)")
    elif features['metro_distance_km'] > 8:
        drivers.append("-5% Limited metro access")
    
    # Government projects
    if features['govt_project_nearby'] == 1:
        drivers.append("+8% Announced infrastructure project boost")
    
    # Age depreciation
    if features['age_years'] > 15:
        pct = min(15, int(features['age_years'] * 0.5))
        drivers.append(f"-{pct}% Age depreciation ({features['age_years']} years old)")
    elif features['age_years'] < 3:
        drivers.append("+6% New property premium")
    
    # Builder reputation
    if features['builder_score'] > 80:
        drivers.append("+5% Premium builder reputation")
    elif features['builder_score'] < 50:
        drivers.append("-4% Below-average builder score")
    
    # Market dynamics
    if features['absorption_rate'] > 0.25:
        drivers.append("+6% High demand micromarket")
    elif features['absorption_rate'] < 0.08:
        drivers.append("-4% Slow-moving market")
    
    # NPA zone
    if features['npa_zone'] == 1:
        drivers.append("-7% High NPA locality risk")
    
    # Supply-demand
    if features['supply_demand_ratio'] > 1.5:
        drivers.append("-5% Oversupply pressure")
    elif features['supply_demand_ratio'] < 0.7:
        drivers.append("+4% Supply shortage premium")
    
    # Price momentum
    if features['price_trend_6m'] > 8:
        drivers.append(f"+4% Strong price momentum ({features['price_trend_6m']:.1f}% growth)")
    elif features['price_trend_6m'] < -5:
        drivers.append(f"-3% Negative price trend ({features['price_trend_6m']:.1f}%)")
    
    # Floor premium
    if features['floor'] >= 10:
        drivers.append("+3% High floor premium")
    
    # IT park proximity (for cities with IT hubs)
    if features['it_park_distance_km'] < 3:
        drivers.append("+4% IT employment hub proximity")
    
    return drivers[:6]  # Return top 6 drivers

def generate_lender_recommendation(
    valuation: Dict, 
    liquidity: Dict, 
    confidence: Dict, 
    fraud_flags: List[Dict]
) -> Dict:
    """Generate lending recommendation"""
    
    market_value_min = valuation['market_value_min']
    distress_value_min = valuation['distress_value_min']
    confidence_score = confidence['score']
    resale_index = liquidity['resale_index']
    
    # Safe loan amount (70% LTV on minimum market value)
    safe_loan_amount = market_value_min * 0.70
    
    # Determine risk level
    high_severity_flags = len([f for f in fraud_flags if f['severity'] == 'HIGH'])
    medium_severity_flags = len([f for f in fraud_flags if f['severity'] == 'MEDIUM'])
    
    if high_severity_flags > 0 or confidence_score < 0.60 or resale_index < 40:
        risk_level = "HIGH"
        decision = "REJECT"
    elif medium_severity_flags > 0 or confidence_score < 0.80 or resale_index < 60:
        risk_level = "MEDIUM"
        decision = "REVIEW"
    else:
        risk_level = "LOW"
        decision = "APPROVE"
    
    # Generate notes
    notes = []
    
    if decision == "APPROVE":
        notes.append(f"Property shows strong fundamentals with {confidence['label']} confidence")
        notes.append(f"Liquidity grade: {liquidity['grade']} - Expected resale in {liquidity['time_to_sell_display']}")
        notes.append(f"Distress recovery assured: {format_currency(distress_value_min)} minimum")
    elif decision == "REVIEW":
        notes.append("Manual review recommended due to:")
        if confidence_score < 0.80:
            notes.append(f"  • Moderate confidence level ({confidence['percentage']})")
        if medium_severity_flags > 0:
            notes.append(f"  • {medium_severity_flags} medium-severity anomaly flag(s)")
        if 40 <= resale_index < 60:
            notes.append(f"  • Medium liquidity (resale index: {resale_index})")
        notes.append("Recommend physical inspection and enhanced due diligence")
    else:  # REJECT
        notes.append("Not recommended for lending due to:")
        if high_severity_flags > 0:
            notes.append(f"  • {high_severity_flags} high-severity fraud flag(s)")
        if confidence_score < 0.60:
            notes.append(f"  • Low confidence score ({confidence['percentage']})")
        if resale_index < 40:
            notes.append(f"  • Poor liquidity (resale index: {resale_index})")
    
    return {
        "safe_loan_amount": round(safe_loan_amount, 0),
        "safe_loan_display": format_currency(safe_loan_amount),
        "ltv_ratio": "70%",
        "distress_recovery_assured": format_currency(distress_value_min),
        "risk_level": risk_level,
        "decision": decision,
        "notes": notes
    }

# API Endpoints

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "PropIntel AI",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "assessment": "/assess",
            "market_data": "/market/{pincode}",
            "health": "/health",
            "documentation": "/docs"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Check if model is loaded
        from engine.valuation import model
        model_status = "loaded" if model is not None else "not_loaded"
    except Exception as e:
        model_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_status": model_status,
        "api_version": "1.0.0"
    }

@app.post("/assess")
def assess_property(property_input: PropertyInput):
    """
    Comprehensive property assessment endpoint with real intelligence layers
    """
    try:
        # Convert input to dictionary
        features = property_input.dict()

        # STEP 1: Geocode address → real lat/long
        geo = geocode_address(features["address"], features["city"])
        features["latitude"] = geo["latitude"]
        features["longitude"] = geo["longitude"]

        # STEP 2: Get real distances from OSM
        if geo["found"]:
            proximity = get_nearby_amenities(geo["latitude"], geo["longitude"])
        else:
            proximity = _fallback_distances()
        
        # Merge proximity into features
        features.update(proximity)

        # STEP 3: Get REAL circle rate for this specific locality
        circle_data = get_circle_rate(
            features["locality"], 
            features["city"],
            "residential" if features.get("property_type") != "commercial" else "commercial"
        )
        features["circle_rate_sqft"] = circle_data["circle_rate_sqft"]
        features["locality_zone"] = circle_data["zone"]

        # STEP 4: Run all engines with real data
        valuation = predict_value(features)
        liquidity = compute_liquidity_v2(features, proximity)
        fraud_flags = detect_fraud(features)
        confidence = compute_confidence(features, fraud_flags)
        
        # Generate existing required features for UI compatibility
        key_drivers = generate_key_drivers(features, valuation)
        lender_rec = generate_lender_recommendation(valuation, liquidity, confidence, fraud_flags)
        doc_verification = {"status": "Pending", "message": "Manual verification required"}

        return {
            "property_summary": f"{features['bhk']}BHK, "
                               f"{features.get('sqft', 0)}sqft, "
                               f"{features['locality']}, {features['city']}",
            "location_resolved": {
                "latitude": geo.get("latitude"),
                "longitude": geo.get("longitude"),
                "circle_rate_zone": circle_data["zone"],
                "circle_rate_sqft": circle_data["circle_rate_sqft"],
                "locality_found_in_db": circle_data["locality_found"]
            },
            "proximity_data": proximity,
            "valuation": valuation,
            "liquidity": liquidity,
            "confidence": confidence,
            "fraud_flags": fraud_flags,
            "document_verification": doc_verification,
            "key_drivers": key_drivers,
            "lender_recommendation": lender_rec,
            "generated_at": datetime.now().isoformat(),
            "model_version": "2.0.0"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment error: {str(e)}")

@app.get("/market/{pincode}")
def get_market_data(pincode: str):
    """
    Get market summary for a pincode
    
    Note: This is a mock endpoint for demo. In production, would query real market database.
    """
    # Mock data generation based on pincode
    pincode_hash = sum(ord(c) for c in pincode)
    
    avg_price = 7000 + (pincode_hash % 8000)
    absorption = 0.10 + (pincode_hash % 25) / 100
    
    demand_level = "HIGH" if absorption > 0.20 else "MEDIUM" if absorption > 0.12 else "LOW"
    
    return {
        "pincode": pincode,
        "avg_price_sqft": avg_price,
        "demand_level": demand_level,
        "absorption_rate": round(absorption, 2),
        "comparable_properties": 15 + (pincode_hash % 35),
        "recommendation": f"Market shows {demand_level.lower()} activity with {absorption*100:.0f}% monthly absorption",
        "data_freshness": "Updated weekly",
        "note": "Mock data for demonstration"
    }

@app.get("/model/info")
def get_model_info():
    """Get information about the trained model"""
    try:
        from engine.valuation import get_model_info
        return get_model_info()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
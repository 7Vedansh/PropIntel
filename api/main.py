"""
PropIntel AI - FastAPI Backend
RESTful API for property valuation and intelligence

Phase 1 refactor:
  • Centralized schemas from api/schemas.py
  • Fixed /health endpoint (was crashing with ImportError)
  • Integrated assess_legal_risk() into assessment pipeline
  • Eliminated duplicate feature aliasing
  • Standardized on carpet_area_sqft / floor_number everywhere
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict
from datetime import datetime
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Centralized schemas
from api.schemas import PropertyAssessmentInput

# Engine imports
from engine.l3_valuation import predict_value, format_currency
from engine.liquidity_v2 import compute_liquidity_v2
from engine.l4_legal import assess_legal_risk
from engine.l5_fraud import detect_fraud
from engine.confidence import compute_confidence
from engine.geocoder import geocode_address
from engine.proximity import get_nearby_amenities, _fallback_distances
from engine.l6_decision import generate_lender_recommendation
from engine.l7_portfolio import compute_portfolio_stress_test
from engine.memo_writer import generate_underwriting_memo
from data.circle_rate_db import get_circle_rate

# ── Structured logging ──
logger = logging.getLogger("propintel.api")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)

# Initialize FastAPI
app = FastAPI(
    title="PropIntel AI",
    description="AI-Powered Property Collateral Valuation & Liquidity Intelligence Engine",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ═══════════════════════════════════════════════════════════════════════════════
# BACKWARD-COMPATIBLE ALIAS
# ═══════════════════════════════════════════════════════════════════════════════
# The old PropertyInput name is kept as an alias so existing dashboard code
# that may import it directly does not break.
PropertyInput = PropertyAssessmentInput

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_key_drivers(features: Dict, valuation: Dict) -> List[str]:
    drivers = []
    # Metro proximity (use standardized field)
    if features.get('metro_distance_km') is not None:
        if features['metro_distance_km'] < 1.5:
            drivers.append("+12% Metro proximity premium (within 1.5km)")
        elif features['metro_distance_km'] > 8:
            drivers.append("-5% Limited metro access")
    # Government projects
    if features.get('govt_project_nearby') == 1:
        drivers.append("+8% Announced infrastructure project boost")
    # Age depreciation
    if features.get('age_years') is not None:
        if features['age_years'] > 15:
            pct = min(15, int(features['age_years'] * 0.5))
            drivers.append(f"-{pct}% Age depreciation ({features['age_years']} years old)")
        elif features['age_years'] < 3:
            drivers.append("+6% New property premium")
    # Builder reputation
    if features.get('builder_score') is not None:
        if features['builder_score'] > 80:
            drivers.append("+5% Premium builder reputation")
        elif features['builder_score'] < 50:
            drivers.append("-4% Below-average builder score")
    # Market dynamics
    if features.get('absorption_rate') is not None:
        if features['absorption_rate'] > 0.25:
            drivers.append("+6% High demand micromarket")
        elif features['absorption_rate'] < 0.08:
            drivers.append("-4% Slow-moving market")
    # NPA zone
    if features.get('npa_zone') == 1:
        drivers.append("-7% High NPA locality risk")
    # Supply-demand
    if features.get('supply_demand_ratio') is not None:
        if features['supply_demand_ratio'] > 1.5:
            drivers.append("-5% Oversupply pressure")
        elif features['supply_demand_ratio'] < 0.7:
            drivers.append("+4% Supply shortage premium")
    # Price momentum
    if features.get('price_trend_6m') is not None:
        if features['price_trend_6m'] > 8:
            drivers.append(f"+4% Strong price momentum ({features['price_trend_6m']:.1f}% growth)")
        elif features['price_trend_6m'] < -5:
            drivers.append(f"-3% Negative price trend ({features['price_trend_6m']:.1f}%)")
    # Floor premium
    if features.get('floor_number') is not None:
        if features['floor_number'] >= 10:
            drivers.append("+3% High floor premium")
    # IT park proximity
    if features.get('it_park_distance_km') is not None:
        if features['it_park_distance_km'] < 3:
            drivers.append("+4% IT employment hub proximity")
    return drivers[:6]

# The logic for generate_lender_recommendation is now strictly decoupled into engine/l6_decision.py


# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "service": "PropIntel AI",
        "version": "2.1.0",
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
    """Health-check endpoint — verifies that the ML model is loadable."""
    try:
        from engine.l3_valuation import _load_models
        models, feature_names = _load_models()
        model_status = "loaded" if models is not None else "not_loaded"
        feature_count = len(feature_names) if feature_names else 0
    except Exception as e:
        model_status = f"error: {str(e)}"
        feature_count = 0
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_status": model_status,
        "feature_count": feature_count,
        "api_version": "2.1.0"
    }

@app.post("/assess")
async def assess_property(property_input: PropertyAssessmentInput):
    """Comprehensive property assessment endpoint with real intelligence layers.

    Executes Layers 1–6 of the PropIntel engine pipeline:
      L1  Geocoding & proximity distance computation
      L2  Circle rate & locality zone lookup
      L3  ML valuation (market + distress ranges)
      L4  Legal risk assessment (ownership, RERA, title)
      L5  Fraud / anomaly detection (9 rules)
      L6  Confidence scoring & lender recommendation
    """
    try:
        # Convert input to dictionary using standardized field names
        features = property_input.model_dump()
        logger.info(
            "Assessment started | locality=%s city=%s bhk=%s sqft=%s",
            features["locality"], features["city"],
            features["bhk"], features["carpet_area_sqft"],
        )

        # ── STEP 1: Geocode address → real lat/long ──
        geo = await geocode_address(features["address"], features["city"])
        features["latitude"] = geo.get("latitude")
        features["longitude"] = geo.get("longitude")

        # ── STEP 2: Get distances from geospatial engine (with fallback) ──
        if geo.get("found"):
            proximity = await get_nearby_amenities(geo["latitude"], geo["longitude"])
            proximity = proximity.copy()
        else:
            proximity = _fallback_distances()

        # Map proximity keys to standardized feature names used by all engines
        features["metro_distance_km"] = proximity.get("distance_to_metro_km", 5.0)
        features["it_park_distance_km"] = proximity.get("distance_to_it_park_km", 5.0)
        features["school_distance_km"] = proximity.get("distance_to_school_km", 1.5)
        features["hospital_distance_km"] = proximity.get("distance_to_hospital_km", 2.0)

        # ── STEP 3: Get circle rate for this locality ──
        circle_data = get_circle_rate(
            features["locality"],
            features["city"],
            "residential" if features.get("property_type") != "commercial" else "commercial"
        )
        features["circle_rate_sqft"] = circle_data["circle_rate_sqft"]
        features["locality_zone"] = circle_data["zone"]

        # ── STEP 4: Run all engine layers ──
        valuation = predict_value(features)
        liquidity = compute_liquidity_v2(features, proximity)
        fraud_flags = detect_fraud(features)
        legal_risk = assess_legal_risk(features)
        confidence = compute_confidence(features, fraud_flags)

        # ── STEP 5: Generate decision outputs ──
        key_drivers = generate_key_drivers(features, valuation)
        lender_rec = generate_lender_recommendation(
            valuation, liquidity, confidence, fraud_flags, legal_risk,
        )
        doc_verification = {"status": "Pending", "message": "Manual verification required"}
        
        # ── Phase 7: Generate AI Underwriter Memo ──
        memo = generate_underwriting_memo(
            features=features,
            valuation=valuation,
            liquidity=liquidity,
            confidence=confidence,
            legal_risk=legal_risk,
            lender_rec=lender_rec
        )

        # ── Build backward-compatible response ──
        response = {
            "property_summary": (
                f"{features['bhk']}BHK, {features.get('carpet_area_sqft', 0)}sqft, "
                f"{features['locality']}, {features['city']}"
            ),
            "location_resolved": {
                "latitude": geo.get("latitude"),
                "longitude": geo.get("longitude"),
                "geocode_source": geo.get("geocode_source", ""),
                "circle_rate_zone": circle_data["zone"],
                "circle_rate_sqft": circle_data["circle_rate_sqft"],
                "locality_found_in_db": circle_data["locality_found"]
            },
            "proximity_data": proximity,
            "valuation": valuation,
            "liquidity": liquidity,
            "confidence": confidence,
            "fraud_flags": fraud_flags,
            "legal_risk": legal_risk,
            "document_verification": doc_verification,
            "key_drivers": key_drivers,
            "lender_recommendation": lender_rec,
            "underwriter_memo": memo,
            "generated_at": datetime.now().isoformat(),
            "model_version": "2.1.0"
        }

        logger.info(
            "Assessment complete | decision=%s confidence=%s resale_index=%s",
            lender_rec["decision"], confidence["score"],
            liquidity["resale_index"],
        )
        return response

    except Exception as e:
        logger.exception("Assessment error")
        raise HTTPException(status_code=500, detail=f"Assessment error: {str(e)}")

@app.post("/api/v1/documents/ingest-and-extract")
async def ingest_and_extract_document(
    file: UploadFile = File(...),
    claims_json: str = Form(..., description="JSON string of property claims")
):
    """
    Phase 6: Document Ingestion, OCR & Discrepancy Pipeline
    Uploads a property document (PDF/Image), runs OCR, extracts ground truth,
    and returns a Discrepancy Matrix against the borrower's claims.
    """
    import json
    from pipeline.ocr_engine import process_document
    from pipeline.entity_extractor import extract_entities
    from pipeline.reconciliation import generate_discrepancy_matrix
    
    try:
        # Parse claims
        claims = json.loads(claims_json)
        
        # Read file bytes
        file_bytes = await file.read()
        
        # 1. OCR / Layout Parser
        raw_text = process_document(file_bytes, file.filename, file.content_type)
        
        # 2. Entity Extraction
        extracted_data = extract_entities(raw_text)
        
        # 3. Reconciliation
        matrix = generate_discrepancy_matrix(claims, extracted_data)
        
        return {
            "filename": file.filename,
            "ocr_status": "SUCCESS",
            "extracted_ground_truth": extracted_data,
            "discrepancy_matrix": matrix.model_dump()
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in claims_json")
    except Exception as e:
        logger.exception("Document processing error")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@app.get("/market/{pincode}")
def get_market_data(pincode: str):
    # Mock data generation based on pincode (unchanged)
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

@app.post("/api/v1/portfolio/stress-test")
async def portfolio_stress_test(portfolio: List[Dict]):
    """
    Phase 7: Portfolio Risk & Stress-Testing Engine
    Receives a list of property loans and returns macroeconomic shock LGDs.
    """
    try:
        results = compute_portfolio_stress_test(portfolio)
        return results
    except Exception as e:
        logger.exception("Portfolio stress test error")
        raise HTTPException(status_code=500, detail=f"Stress test error: {str(e)}")

@app.get("/model/info")
def get_model_info():
    try:
        from engine.valuation import get_model_info
        return get_model_info()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
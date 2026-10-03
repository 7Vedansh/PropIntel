"""
PropIntel AI — Centralized Pydantic Schemas
=============================================
All request/response domain models live here for reuse across
API endpoints, engine layers, and test fixtures.

Uses Pydantic v2 model_validator / field_validator syntax.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class PropertyType(str, Enum):
    APARTMENT = "apartment"
    VILLA = "villa"
    INDEPENDENT_HOUSE = "independent_house"
    COMMERCIAL = "commercial"


class OwnershipType(str, Enum):
    FREEHOLD = "freehold"
    LEASEHOLD = "leasehold"
    DISPUTED = "disputed"


class DecisionVerdict(str, Enum):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    REJECT = "REJECT"


class RiskGrade(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class FraudSeverity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class PropertyAssessmentInput(BaseModel):
    """Input model for property collateral assessment.

    Uses standardized field names (carpet_area_sqft, floor_number)
    that are consistent across all engine layers.
    """

    # ── Location identifiers ──
    address: str = Field(
        ..., min_length=5, max_length=500,
        description="Full property address",
        examples=["A-101, Signature Towers, Baner Road"]
    )
    locality: str = Field(
        ..., min_length=2, max_length=100,
        description="Property locality/area name",
        examples=["Baner"]
    )
    city: str = Field(
        ..., min_length=2, max_length=50,
        description="City name",
        examples=["Pune"]
    )

    # ── Physical property attributes ──
    bhk: int = Field(..., ge=1, le=4, description="Number of bedrooms (1–4)")
    carpet_area_sqft: float = Field(
        ..., ge=100, le=10000,
        description="RERA carpet area in square feet"
    )
    age_years: int = Field(..., ge=0, le=80, description="Property age in years")
    floor_number: int = Field(..., ge=0, le=60, description="Floor number (0 = ground)")
    total_floors: int = Field(..., ge=1, le=60, description="Total floors in building")

    # ── Property classification ──
    property_type: PropertyType = Field(
        default=PropertyType.APARTMENT,
        description="Property classification"
    )
    furnishing: str = Field(default="semi", description="Furnishing status")
    parking: int = Field(default=1, ge=0, le=5, description="Number of parking spots")
    ownership_type: OwnershipType = Field(
        default=OwnershipType.FREEHOLD,
        description="Ownership tenure type"
    )
    has_rera: int = Field(default=1, ge=0, le=1, description="RERA registration (0/1)")
    has_lift: Optional[bool] = Field(default=True, description="Lift availability")

    # ── Market & builder parameters (looked up internally if not provided) ──
    builder_score: int = Field(..., ge=0, le=100, description="Builder RERA reputation score (0–100)")
    govt_project_nearby: int = Field(..., ge=0, le=1, description="Government infrastructure project announced (0/1)")
    npa_zone: int = Field(default=0, ge=0, le=1, description="High NPA locality flag (0/1)")
    supply_demand_ratio: float = Field(..., ge=0.1, le=5.0, description="Supply-to-demand ratio")
    price_trend_6m: float = Field(..., ge=-20, le=30, description="6-month locality price trend (%)")

    # ── Optional override distances (auto-computed by geospatial engine if omitted) ──
    metro_distance_km: Optional[float] = Field(None, ge=0.1, le=20, description="Distance to nearest metro (km)")
    it_park_distance_km: Optional[float] = Field(None, ge=0.1, le=30, description="Distance to nearest IT park (km)")
    school_distance_km: Optional[float] = Field(None, ge=0.1, le=10, description="Distance to nearest school (km)")
    hospital_distance_km: Optional[float] = Field(None, ge=0.1, le=15, description="Distance to nearest hospital (km)")
    circle_rate_sqft: Optional[float] = Field(None, ge=1000, le=100000, description="Govt circle rate per sqft (auto-looked up if omitted)")
    absorption_rate: Optional[float] = Field(None, ge=0.01, le=0.99, description="Monthly absorption rate (0–1)")
    
    # ── Phase 5 Fields (For 4-Vector Fraud Check) ──
    actual_price_sqft: Optional[float] = Field(None, description="Actual claimed transaction price per sqft")
    verified_carpet_area_sqft: Optional[float] = Field(None, description="Verified carpet area from Title Deed")

    @field_validator("floor_number")
    @classmethod
    def floor_must_not_exceed_total(cls, v, info):
        total = info.data.get("total_floors")
        if total is not None and v > total:
            raise ValueError("floor_number cannot exceed total_floors")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "address": "A-101, Signature Towers",
                    "locality": "Baner",
                    "city": "Pune",
                    "bhk": 2,
                    "carpet_area_sqft": 1200,
                    "age_years": 8,
                    "floor_number": 7,
                    "total_floors": 14,
                    "property_type": "apartment",
                    "furnishing": "semi",
                    "parking": 1,
                    "ownership_type": "freehold",
                    "has_rera": 1,
                    "has_lift": True,
                    "builder_score": 78,
                    "govt_project_nearby": 1,
                    "npa_zone": 0,
                    "supply_demand_ratio": 0.85,
                    "price_trend_6m": 6.5,
                }
            ]
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# RESPONSE SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class LocationResolved(BaseModel):
    latitude: float
    longitude: float
    geocode_source: str = ""
    circle_rate_zone: str = ""
    circle_rate_sqft: float = 0.0
    locality_found_in_db: bool = False


class ProximityData(BaseModel):
    distance_to_metro_km: float = 5.0
    distance_to_highway_km: float = 3.0
    distance_to_hospital_km: float = 2.0
    distance_to_school_km: float = 1.5
    distance_to_mall_km: float = 3.0
    distance_to_it_park_km: float = 5.0
    amenity_counts: Dict[str, int] = {}


class SHAPAttribution(BaseModel):
    feature: str
    impact_sqft: str
    direction: str  # "positive" or "negative"


class ValuationOutput(BaseModel):
    price_per_sqft: float
    market_value_min: float
    market_value_max: float
    distress_value_min: float
    distress_value_max: float
    market_value_display: str
    distress_value_display: str
    shap_attributions: List[SHAPAttribution] = []


class SurvivalPoint(BaseModel):
    days: int
    prob_sold: float


class LiquidityOutput(BaseModel):
    resale_index: float
    grade: RiskGrade
    time_to_sell_min_days: int
    time_to_sell_max_days: int
    time_to_sell_display: str
    absorption_rate_pct: str
    liquidity_drivers: List[str] = []
    factor_breakdown: List[Dict[str, Any]] = []
    survival_curve: List[SurvivalPoint] = []


class FraudFlag(BaseModel):
    code: str
    severity: FraudSeverity
    message: str
    recommendation: str = ""


class LegalRiskOutput(BaseModel):
    legal_risk_score: int = 0
    legal_risk_grade: RiskGrade = RiskGrade.LOW
    legal_flags: List[FraudFlag] = []


class ConfidenceOutput(BaseModel):
    score: float
    percentage: str
    label: RiskGrade
    breakdown: Dict[str, float] = {}
    interpretation: str = ""
    concerns: List[str] = []


class UnderwritingDecision(BaseModel):
    decision: DecisionVerdict
    risk_level: RiskGrade
    safe_loan_amount: float
    safe_loan_display: str
    ltv_ratio: str = "70%"
    distress_recovery_assured: str
    notes: List[str] = []


class DiscrepancyItem(BaseModel):
    parameter: str
    claimed: str
    extracted: str
    variance_pct: str
    status: str  # "VERIFIED", "FLAGGED", "MISSING"
    severity: FraudSeverity = FraudSeverity.LOW


class DiscrepancyMatrix(BaseModel):
    has_mismatch: bool = False
    items: List[DiscrepancyItem] = []


class AssessmentResponse(BaseModel):
    """Unified response payload for POST /assess.

    Backward-compatible with existing dashboard fields while adding
    new structured outputs (legal risk, discrepancy matrix, SHAP).
    """
    property_summary: str
    location_resolved: LocationResolved
    proximity_data: ProximityData
    valuation: ValuationOutput
    liquidity: LiquidityOutput
    confidence: ConfidenceOutput
    fraud_flags: List[FraudFlag]
    legal_risk: LegalRiskOutput
    document_verification: Dict[str, str]
    discrepancy_matrix: DiscrepancyMatrix = DiscrepancyMatrix()
    key_drivers: List[str]
    lender_recommendation: UnderwritingDecision
    underwriter_memo: Dict[str, Any] = {}
    generated_at: str
    model_version: str = "2.1.0"

    model_config = {"protected_namespaces": ()}


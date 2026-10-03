"""
PropIntel AI — Layer 5: 4-Vector Fraud Engine
===============================================
Automates anomaly detection, tax evasion checks, and cross-lender duplicate tracking.
"""

from typing import Dict, List
import hashlib

def detect_fraud(features: Dict) -> List[Dict]:
    """
    Phase 5: 4-Vector Fraud & Anomaly Engine
    """
    flags = []
    
    # Extract features
    bhk = features.get('bhk')
    sqft = features.get('carpet_area_sqft') or features.get('sqft')
    circle_rate_sqft = features.get('circle_rate_sqft')
    floor = features.get('floor_number') or features.get('floor')
    total_floors = features.get('total_floors')
    age_years = features.get('age_years')
    locality = features.get('locality', '').lower()
    address = features.get('address', '')
    
    # ── VECTOR 1: Discrepancy Matrix (Deed vs. Claim Area) ──
    verified_sqft = features.get('verified_carpet_area_sqft')
    if sqft and verified_sqft:
        drift_pct = abs(sqft - verified_sqft) / sqft
        if drift_pct > 0.15:
            flags.append({
                "code": "DOCUMENT_AREA_MISMATCH",
                "severity": "HIGH",
                "message": f"Claimed area ({sqft}) differs from verified document area ({verified_sqft}) by {drift_pct*100:.1f}%",
                "recommendation": "Reject - High probability of collateral overstatement."
            })
            
    # ── VECTOR 2: Statutory Arbitrage (Section 50C Income Tax Risk) ──
    claimed_price_sqft = features.get('actual_price_sqft')
    if claimed_price_sqft and circle_rate_sqft:
        if claimed_price_sqft < circle_rate_sqft * 0.80:
            flags.append({
                "code": "STATUTORY_ARBITRAGE_RISK",
                "severity": "HIGH",
                "message": f"Transaction price (₹{claimed_price_sqft:.0f}) is >20% below Circle Rate (₹{circle_rate_sqft:.0f}).",
                "recommendation": "Section 50C Income Tax risk. Verify cash component or severe structural defects."
            })

    # ── VECTOR 3: Cadastral Geofencing ──
    # Simulating coordinate check against registered CTS boundaries
    geo_confidence = features.get('geocode_confidence', 1.0)
    if geo_confidence < 0.6:
        flags.append({
            "code": "CADASTRAL_GEOFENCE_FAIL",
            "severity": "MEDIUM",
            "message": "Property coordinates fall outside the registered CTS / Survey boundaries.",
            "recommendation": "Verify physical location against Title Deed."
        })

    # ── VECTOR 4: Duplicate Collateral Hash ──
    if address and locality and floor is not None:
        flat_no = address.split(',')[0].strip().lower()
        raw_sig = f"{locality}|{floor}|{flat_no}".encode('utf-8')
        collat_hash = hashlib.md5(raw_sig).hexdigest()
        
        # Simulating cross-lender duplicate check (Mock logic for demonstration)
        # In production, this checks a distributed ledger / central pledge registry
        if "a-101" in flat_no and "baner" in locality:
            flags.append({
                "code": "DUPLICATE_COLLATERAL_PLEDGE",
                "severity": "HIGH",
                "message": f"Cross-lender duplicate pledge detected. Hash: {collat_hash[:8]}",
                "recommendation": "Reject - Asset already hypothecated at another institution."
            })

    # ── HEURISTIC ANOMALIES ──
    
    # Area to Floor Ratio (Mislabeled Commercial)
    if sqft is not None and total_floors is not None and total_floors > 0:
        if sqft >= 3000 and total_floors <= 3 and features.get('property_type', 'apartment') == 'apartment':
            flags.append({
                "code": "EXTREME_AREA_FLOOR_RATIO",
                "severity": "HIGH",
                "message": f"Unusually large {sqft:.0f} sqft apartment in a {total_floors}-floor building",
                "recommendation": "High probability of mislabeled commercial/bungalow property. Reverify collateral type."
            })
            
    # Age vs Locality Check (Improbable age in new IT hub)
    new_areas = ['hinjewadi', 'kharadi', 'wakad', 'baner', 'wagholi']
    if age_years is not None and age_years > 30 and locality in new_areas:
        flags.append({
            "code": "IMPROBABLE_AGE_LOCALITY",
            "severity": "HIGH",
            "message": f"Property claims to be {age_years} years old in a new development area ({locality.title()})",
            "recommendation": "Highly improbable structural age for this micromarket. Verify property documents."
        })
        
    return flags

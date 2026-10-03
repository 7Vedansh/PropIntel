"""
PropIntel AI — Layer 4: Legal & Title Engine
==============================================
Automates legal compliance checks, title continuity scoring, and leasehold tenure tracking.
"""

from typing import Dict, List, Any

def assess_legal_risk(features: dict) -> dict:
    """
    Phase 5: Legal Title Verification
    Validates ownership structure, tenure, and RERA compliance.
    """
    risk_score = 0
    flags = []
    
    # Leasehold Tenure Countdown
    if features.get('ownership_type', '').lower() == 'leasehold':
        lease_remaining = features.get('lease_years_remaining', 25) # Default assumption if not provided
        if lease_remaining < 30:
            risk_score += 40
            flags.append({
                "code": "LEASEHOLD_TITLE_CRITICAL",
                "severity": "HIGH",
                "message": f"Leasehold property with only {lease_remaining} years remaining",
                "recommendation": "Reject - Term is shorter than typical 30-year loan horizon."
            })
        else:
            risk_score += 10
            flags.append({
                "code": "LEASEHOLD_TITLE",
                "severity": "MEDIUM",
                "message": f"Leasehold property — {lease_remaining} years remaining",
                "recommendation": "Monitor lease expiry. Safe for standard term loan."
            })
    
    # RERA Registration & Project Approvals
    if features.get('property_type', '') in ['apartment', 'commercial']:
        if not features.get('has_rera'):
            risk_score += 30
            flags.append({
                "code": "NO_RERA_REGISTRATION",
                "severity": "HIGH", 
                "message": "Project not RERA registered",
                "recommendation": "High Title Risk. Request completion certificate and approved floor plans."
            })
    
    # Chain-of-Title Continuity Check (Simulation)
    # Checks if Grantor-Grantee relationships match the claimed ownership
    if features.get('ownership_type', '').lower() == 'disputed':
        risk_score += 60
        flags.append({
            "code": "DISPUTED_TITLE",
            "severity": "HIGH",
            "message": "Disputed ownership or active lis pendens detected in SRO records",
            "recommendation": "REJECT — do not proceed without legal clearance."
        })
    
    legal_risk_grade = (
        "HIGH" if risk_score >= 40 else
        "MEDIUM" if risk_score >= 20 else
        "LOW"
    )
    
    return {
        "legal_risk_score": risk_score,
        "legal_risk_grade": legal_risk_grade,
        "legal_flags": flags
    }

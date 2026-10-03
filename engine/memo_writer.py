"""
PropIntel AI — AI Underwriter Summary Writer
=============================================
Generates structured, regulatory-compliant Underwriting Memorandums.
"""

from typing import Dict, Any, List

def generate_underwriting_memo(
    features: Dict[str, Any],
    valuation: Dict[str, Any],
    liquidity: Dict[str, Any],
    confidence: Dict[str, Any],
    legal_risk: Dict[str, Any],
    lender_rec: Dict[str, Any],
    discrepancy_matrix: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Synthesizes all 7 Engine Layers into a single, cohesive Credit Committee Memo.
    """
    
    memo = {
        "memo_title": f"Collateral Intelligence Memo - {features.get('locality', 'Unknown Locality')}",
        "executive_summary": "",
        "valuation_summary": "",
        "risk_and_liquidity": "",
        "conditions_precedent": []
    }
    
    # 1. Executive Summary
    decision = lender_rec.get('decision', 'REVIEW')
    safe_loan = lender_rec.get('safe_loan_display', 'N/A')
    memo["executive_summary"] = (
        f"The AI Underwriter recommends a {decision} decision for the {features.get('property_type', 'property')} "
        f"located at {features.get('address')}. The maximum safe sanction cap is {safe_loan}, "
        f"yielding an effective LTV of {lender_rec.get('ltv_ratio', 'N/A')}."
    )
    
    # 2. Valuation Summary
    market_val = valuation.get('market_value_display', 'N/A')
    distress_val = valuation.get('distress_value_display', 'N/A')
    conf_label = confidence.get('label', 'UNKNOWN')
    memo["valuation_summary"] = (
        f"Fair Market Value is estimated at {market_val}, with a Distress Floor of {distress_val}. "
        f"The Valuation Confidence Engine scores this appraisal as {conf_label} ({confidence.get('percentage', 'N/A')})."
    )
    
    # 3. Risk and Liquidity
    liq_grade = liquidity.get('grade', 'UNKNOWN')
    days_to_sell = liquidity.get('time_to_sell_display', 'N/A')
    legal_grade = legal_risk.get('legal_risk_grade', 'UNKNOWN')
    
    memo["risk_and_liquidity"] = (
        f"Liquidity Profile is {liq_grade}, with an estimated time-to-liquidate of {days_to_sell}. "
        f"Title & Legal Risk is graded as {legal_grade}. "
    )
    if legal_grade in ["HIGH", "MEDIUM"]:
        memo["risk_and_liquidity"] += " Caution is advised regarding title encumbrances or leasehold tenure."
        
    # 4. Conditions Precedent (CPs)
    cps = []
    if decision != "APPROVE":
        cps.extend(lender_rec.get('notes', []))
        
    if discrepancy_matrix and discrepancy_matrix.get('has_mismatch'):
        cps.append("Resolve OCR Document Discrepancy Matrix flags before final sanction.")
        
    if legal_grade == "HIGH":
        cps.append("Obtain independent legal counsel clearance on title continuity.")
        
    if confidence.get('score', 1.0) < 0.70:
        cps.append("Conduct physical valuation site visit due to low AI confidence score.")
        
    if not cps:
        cps.append("Standard KYC and Income documentation verification.")
        
    memo["conditions_precedent"] = cps
    
    return memo

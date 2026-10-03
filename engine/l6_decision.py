"""
PropIntel AI — Layer 6: Liquidity Survival & Sanction Sizing Engine
=====================================================================
Models empirical Time-to-Liquidate probability curves and determines safe loan sanction caps.
"""

from typing import Dict, List
from engine.l3_valuation import format_currency

def generate_lender_recommendation(
    valuation: Dict,
    liquidity: Dict,
    confidence: Dict,
    fraud_flags: List[Dict],
    legal_risk: Dict,
) -> Dict:
    """
    Phase 4: Dynamic LTV & Sanction Sizing Policy
    Calculates dynamic sanction cap and issues decision based on risk rules.
    """
    market_value_min = valuation['market_value_min']
    distress_value_min = valuation['distress_value_min']
    confidence_score = confidence['score']
    resale_index = liquidity['resale_index']
    legal_grade = legal_risk.get('legal_risk_grade', 'LOW')

    # Sanction Cap = min(Market Value Q0.50 * Policy LTV, Distress Value Q0.10 * 0.90)
    policy_ltv = 0.75  # 75% baseline LTV policy
    safe_loan_amount = min(market_value_min * policy_ltv, distress_value_min * 0.90)

    high_severity_flags = len([f for f in fraud_flags if f['severity'] == 'HIGH'])
    medium_severity_flags = len([f for f in fraud_flags if f['severity'] == 'MEDIUM'])

    # Decision Matrix based on multiple risk vectors
    if (high_severity_flags > 0 or confidence_score < 0.60
            or resale_index < 40 or legal_grade == "HIGH"):
        risk_level = "HIGH"
        decision = "REJECT"
    elif (medium_severity_flags > 0 or confidence_score < 0.80
            or resale_index < 60 or legal_grade == "MEDIUM"):
        risk_level = "MEDIUM"
        decision = "REVIEW"
    else:
        risk_level = "LOW"
        decision = "APPROVE"

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
        if legal_grade == "MEDIUM":
            notes.append("  • Moderate legal/title risk — verify ownership documents")
        notes.append("Recommend physical inspection and enhanced due diligence")
    else:
        notes.append("Not recommended for lending due to:")
        if high_severity_flags > 0:
            notes.append(f"  • {high_severity_flags} high-severity fraud flag(s)")
        if confidence_score < 0.60:
            notes.append(f"  • Low confidence score ({confidence['percentage']})")
        if resale_index < 40:
            notes.append(f"  • Poor liquidity (resale index: {resale_index})")
        if legal_grade == "HIGH":
            notes.append("  • High legal/title risk — disputed or encumbered title")

    effective_ltv = (safe_loan_amount / market_value_min) * 100

    return {
        "safe_loan_amount": round(safe_loan_amount, 0),
        "safe_loan_display": format_currency(safe_loan_amount),
        "ltv_ratio": f"{effective_ltv:.1f}%",
        "distress_recovery_assured": format_currency(distress_value_min),
        "risk_level": risk_level,
        "decision": decision,
        "notes": notes
    }

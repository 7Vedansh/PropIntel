"""
PropIntel AI — Document Reconciliation Engine
=============================================
Cross-compares OCR extracted ground truth with borrower application claims.
Generates the structured DiscrepancyMatrix.
"""

from typing import Dict, Any
from api.schemas import DiscrepancyMatrix, DiscrepancyItem, FraudSeverity

def generate_discrepancy_matrix(claims: Dict[str, Any], extracted: Dict[str, Any]) -> DiscrepancyMatrix:
    """
    Compares claimed values with verified OCR extracted values.
    Returns a Pydantic DiscrepancyMatrix object.
    """
    items = []
    has_mismatch = False

    # 1. Carpet Area Reconciliation
    claimed_sqft = claims.get('carpet_area_sqft')
    verified_sqft = extracted.get('verified_carpet_area_sqft')
    
    if claimed_sqft and verified_sqft:
        variance = abs(claimed_sqft - verified_sqft) / claimed_sqft
        status = "FLAGGED" if variance > 0.05 else "VERIFIED"
        severity = FraudSeverity.HIGH if variance > 0.15 else (FraudSeverity.MEDIUM if variance > 0.05 else FraudSeverity.LOW)
        
        if status == "FLAGGED":
            has_mismatch = True
            
        items.append(DiscrepancyItem(
            parameter="Carpet Area (sqft)",
            claimed=str(claimed_sqft),
            extracted=str(verified_sqft),
            variance_pct=f"{variance*100:.1f}%",
            status=status,
            severity=severity
        ))
    elif claimed_sqft:
        items.append(DiscrepancyItem(
            parameter="Carpet Area (sqft)",
            claimed=str(claimed_sqft),
            extracted="Not Found in Document",
            variance_pct="N/A",
            status="MISSING",
            severity=FraudSeverity.MEDIUM
        ))

    # 2. Consideration / Transaction Price
    claimed_price = claims.get('total_consideration')
    verified_price = extracted.get('total_consideration')
    
    if claimed_price and verified_price:
        variance = abs(claimed_price - verified_price) / claimed_price
        # Price should match exactly or very closely
        status = "FLAGGED" if variance > 0.02 else "VERIFIED"
        severity = FraudSeverity.HIGH if variance > 0.02 else FraudSeverity.LOW
        
        if status == "FLAGGED":
            has_mismatch = True
            
        items.append(DiscrepancyItem(
            parameter="Transaction Consideration",
            claimed=f"₹{claimed_price}",
            extracted=f"₹{verified_price}",
            variance_pct=f"{variance*100:.1f}%",
            status=status,
            severity=severity
        ))

    # 3. Ownership / Applicant Name (If available in claims)
    claimed_owner = claims.get('applicant_name')
    verified_owner = extracted.get('verified_owner')
    
    if claimed_owner and verified_owner:
        # Simple string compare
        if claimed_owner.lower().strip() != verified_owner.lower().strip():
            has_mismatch = True
            items.append(DiscrepancyItem(
                parameter="Owner Name",
                claimed=claimed_owner,
                extracted=verified_owner,
                variance_pct="Mismatch",
                status="FLAGGED",
                severity=FraudSeverity.HIGH
            ))
        else:
            items.append(DiscrepancyItem(
                parameter="Owner Name",
                claimed=claimed_owner,
                extracted=verified_owner,
                variance_pct="0%",
                status="VERIFIED",
                severity=FraudSeverity.LOW
            ))

    matrix = DiscrepancyMatrix(
        has_mismatch=has_mismatch,
        items=items
    )
    
    return matrix

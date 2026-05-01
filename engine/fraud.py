"""
PropIntel AI - Fraud Detection Engine
Rule-based anomaly detection for property data validation
"""

from typing import Dict, List

def detect_fraud(features: Dict) -> List[Dict]:
    """
    Detect potential fraud or data anomalies using rule-based checks
    
    Args:
        features: Property features dictionary
        
    Returns:
        List of fraud flag dictionaries
    """
    flags = []
    
    # Extract features
    bhk = features['bhk']
    sqft = features['sqft']
    circle_rate_sqft = features['circle_rate_sqft']
    floor = features['floor']
    total_floors = features['total_floors']
    age_years = features['age_years']
    builder_score = features['builder_score']
    absorption_rate = features['absorption_rate']
    price_trend_6m = features['price_trend_6m']
    npa_zone = features['npa_zone']
    supply_demand_ratio = features['supply_demand_ratio']
    
    # RULE 1: Size Sanity Check
    size_ranges = {
        1: (400, 700),
        2: (800, 1400),
        3: (1300, 2200),
        4: (2000, 4000)
    }
    
    if bhk in size_ranges:
        min_sqft, max_sqft = size_ranges[bhk]
        
        if sqft > max_sqft * 2.2:
            flags.append({
                "code": "SIZE_ANOMALY_HIGH",
                "severity": "HIGH",
                "message": f"Claimed {sqft:.0f} sqft for {bhk}BHK — {(sqft/max_sqft):.1f}x locality average of {max_sqft} sqft",
                "recommendation": "Request physical inspection and floor plan documents"
            })
        elif sqft < min_sqft * 0.5:
            flags.append({
                "code": "SIZE_ANOMALY_LOW",
                "severity": "HIGH",
                "message": f"Claimed {sqft:.0f} sqft for {bhk}BHK — only {(sqft/min_sqft*100):.0f}% of typical {min_sqft} sqft",
                "recommendation": "Verify property documents and actual carpet area"
            })
    
    # RULE 2: Price vs Circle Rate
    # Valuation significantly below government rate is suspicious
    if 'actual_price_sqft' in features:
        claimed_price = features['actual_price_sqft']
        if claimed_price < circle_rate_sqft * 0.75:
            flags.append({
                "code": "BELOW_STATUTORY_FLOOR",
                "severity": "HIGH",
                "message": f"Claimed price Rs. {claimed_price:.0f}/sqft is {((1 - claimed_price/circle_rate_sqft)*100):.0f}% below circle rate of Rs. {circle_rate_sqft:.0f}/sqft",
                "recommendation": "Investigate reason for significant discount; verify no legal/structural issues"
            })
    
    # RULE 3: Floor vs Building Height
    if floor > total_floors:
        flags.append({
            "code": "FLOOR_EXCEEDS_BUILDING",
            "severity": "HIGH",
            "message": f"Property on floor {floor} but building has only {total_floors} floors",
            "recommendation": "Critical data error - verify property documents"
        })
    
    # RULE 4: Age vs Condition Consistency
    if age_years < 3 and builder_score < 45:
        flags.append({
            "code": "NEW_PROPERTY_LOW_BUILDER_SCORE",
            "severity": "MEDIUM",
            "message": f"Property is {age_years} years old but builder has low reputation score of {builder_score}/100",
            "recommendation": "Check RERA records and builder delivery history"
        })
    
    # RULE 5: Absorption vs Price Trend Conflict
    if absorption_rate < 0.05 and price_trend_6m > 10:
        flags.append({
            "code": "MARKET_SIGNAL_CONFLICT",
            "severity": "MEDIUM",
            "message": f"Low absorption rate ({absorption_rate*100:.1f}%) contradicts high price growth ({price_trend_6m:.1f}%)",
            "recommendation": "Verify listing data; possible speculative pricing not backed by demand"
        })
    
    # RULE 6: NPA Zone with High Demand Claims
    if npa_zone == 1 and supply_demand_ratio < 0.6:
        flags.append({
            "code": "NPA_ZONE_DEMAND_CONFLICT",
            "severity": "MEDIUM",
            "message": f"Property in high-NPA zone but claims strong demand (S/D ratio: {supply_demand_ratio:.2f})",
            "recommendation": "Conduct enhanced due diligence on locality and recent transactions"
        })
    
    # RULE 7: Extreme Age
    if age_years > 50:
        flags.append({
            "code": "VERY_OLD_PROPERTY",
            "severity": "LOW",
            "message": f"Property is {age_years} years old - structural assessment needed",
            "recommendation": "Require structural stability certificate and renovation history"
        })
    
    # RULE 8: Floor Consistency
    if floor == 0:
        flags.append({
            "code": "GROUND_FLOOR_ALERT",
            "severity": "LOW",
            "message": "Ground floor property - typically lower valuation and liquidity",
            "recommendation": "Apply standard ground floor discount in valuation"
        })
    
    # RULE 9: Very High Floor
    if floor > 15 and total_floors - floor > 10:
        # High floor but not a top floor
        flags.append({
            "code": "HIGH_FLOOR_MIDDLE",
            "severity": "LOW",
            "message": f"High floor ({floor}) in very tall building ({total_floors} floors)",
            "recommendation": "Verify elevator access and premium justification"
        })
    
    return flags
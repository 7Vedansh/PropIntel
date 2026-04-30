"""
PropIntel AI - Confidence Scoring Engine
Calculates reliability score for valuation outputs
"""

from typing import Dict, List

def compute_confidence(features: Dict, fraud_flags: List[Dict]) -> Dict:
    """
    Compute confidence score based on data quality, signal agreement, and anomalies
    
    Args:
        features: Property features dictionary
        fraud_flags: List of detected fraud/anomaly flags
        
    Returns:
        Dictionary with confidence score, breakdown, and interpretation
    """
    
    # 1. Data Completeness Score (40% weight)
    critical_fields = [
        'age_years', 'floor', 'builder_score', 'absorption_rate',
        'metro_distance_km', 'circle_rate_sqft', 'price_trend_6m', 
        'supply_demand_ratio'
    ]
    
    complete_count = 0
    for field in critical_fields:
        value = features.get(field)
        # Check if field exists and is not null/zero (except where zero is valid)
        if value is not None:
            if field in ['govt_project_nearby', 'npa_zone']:
                # Binary fields - any value is valid
                complete_count += 1
            elif value != 0 or field == 'floor':  # Floor can legitimately be 0
                complete_count += 1
    
    data_completeness = complete_count / len(critical_fields)
    
    # 2. Signal Agreement Score (30% weight)
    # Check if market signals are consistent
    absorption_rate = features.get('absorption_rate', 0.15)
    price_trend_6m = features.get('price_trend_6m', 0)
    supply_demand_ratio = features.get('supply_demand_ratio', 1.0)
    
    # Normalize absorption rate to market average (0.15)
    absorption_ratio = absorption_rate / 0.15
    
    # Check for consistency between signals
    signal_consistency = 1.0
    
    # Absorption and price trend should align
    if (absorption_rate > 0.20 and price_trend_6m < -3) or \
       (absorption_rate < 0.08 and price_trend_6m > 8):
        signal_consistency *= 0.7  # Conflicting signals
    
    # Supply-demand and absorption should align
    if (supply_demand_ratio > 1.5 and absorption_rate > 0.25) or \
       (supply_demand_ratio < 0.7 and absorption_rate < 0.08):
        signal_consistency *= 0.75  # Conflicting signals
    
    # Overall signal agreement
    if 0.7 < absorption_ratio < 1.6 and signal_consistency > 0.85:
        signal_agreement = 1.0
    else:
        signal_agreement = 0.55 * signal_consistency
    
    # 3. Anomaly Score (30% weight)
    # Penalize based on fraud flag severity
    anomaly_penalty = 0.0
    
    severity_weights = {
        'HIGH': 0.25,
        'MEDIUM': 0.12,
        'LOW': 0.05
    }
    
    for flag in fraud_flags:
        severity = flag.get('severity', 'LOW')
        anomaly_penalty += severity_weights.get(severity, 0.05)
    
    anomaly_score = max(0.0, 1.0 - anomaly_penalty)
    
    # 4. Calculate Overall Confidence
    confidence_score = (
        0.40 * data_completeness +
        0.30 * signal_agreement +
        0.30 * anomaly_score
    )
    
    # Determine confidence label
    if confidence_score > 0.80:
        label = "HIGH"
        interpretation = "High confidence. All data signals consistent. Safe for automated lending decision."
    elif confidence_score >= 0.60:
        label = "MEDIUM"
        interpretation = "Medium confidence. Some data gaps or signal inconsistencies. Recommend manual review."
    else:
        label = "LOW"
        interpretation = "Low confidence. Significant data issues or anomalies detected. Requires thorough manual verification."
    
    # Add specific concerns
    concerns = []
    if data_completeness < 0.80:
        concerns.append("Missing or incomplete critical data fields")
    if signal_agreement < 0.70:
        concerns.append("Market signals show inconsistencies")
    if len(fraud_flags) > 0:
        concerns.append(f"{len(fraud_flags)} anomaly flag(s) detected")
    
    return {
        "score": round(confidence_score, 2),
        "percentage": f"{round(confidence_score * 100)}%",
        "label": label,
        "breakdown": {
            "data_completeness": round(data_completeness, 2),
            "signal_agreement": round(signal_agreement, 2),
            "anomaly_score": round(anomaly_score, 2)
        },
        "interpretation": interpretation,
        "concerns": concerns if concerns else ["No major concerns identified"]
    }
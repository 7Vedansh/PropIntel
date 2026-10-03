"""
PropIntel AI — Layer 7: Portfolio Risk & Stress-Testing Engine
================================================================
Simulates macroeconomic shock scenarios and computes portfolio-level risk metrics.
"""

from typing import List, Dict, Any

def compute_portfolio_stress_test(portfolio: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Simulates macroeconomic shocks across a portfolio of collateral assets.
    """
    total_exposure = 0
    total_market_value = 0
    total_distress_value = 0
    
    # Macroeconomic Shock Scenarios
    shock_scenarios = {
        "baseline": {"market_correction": 0.0, "interest_rate_spike": 0.0},
        "moderate_stress": {"market_correction": -0.15, "interest_rate_spike": 0.02}, # -15% property value, +200bps
        "severe_stress": {"market_correction": -0.30, "interest_rate_spike": 0.05}  # -30% property value, +500bps
    }
    
    # Concentration metrics
    locality_exposure = {}
    builder_exposure = {}
    
    for asset in portfolio:
        exposure = asset.get('loan_amount', 0)
        mv = asset.get('market_value', 0)
        dv = asset.get('distress_value', 0)
        locality = asset.get('locality', 'Unknown')
        builder = asset.get('builder', 'Unknown')
        
        total_exposure += exposure
        total_market_value += mv
        total_distress_value += dv
        
        locality_exposure[locality] = locality_exposure.get(locality, 0) + exposure
        builder_exposure[builder] = builder_exposure.get(builder, 0) + exposure

    # Compute Herfindahl-Hirschman Index (HHI) for concentration
    # HHI = Sum of squared market shares
    if total_exposure > 0:
        hhi_locality = sum((v / total_exposure * 100) ** 2 for v in locality_exposure.values())
        hhi_builder = sum((v / total_exposure * 100) ** 2 for v in builder_exposure.values())
    else:
        hhi_locality = 0
        hhi_builder = 0

    results = {
        "portfolio_summary": {
            "total_assets": len(portfolio),
            "total_exposure": total_exposure,
            "total_market_value": total_market_value,
            "weighted_average_ltv": (total_exposure / total_market_value) if total_market_value > 0 else 0
        },
        "concentration_risk": {
            "geographic_hhi": hhi_locality,
            "geographic_hhi_status": "HIGH RISK" if hhi_locality > 2500 else ("MODERATE" if hhi_locality > 1500 else "LOW RISK"),
            "builder_hhi": hhi_builder,
            "builder_hhi_status": "HIGH RISK" if hhi_builder > 2500 else ("MODERATE" if hhi_builder > 1500 else "LOW RISK")
        },
        "stress_test_scenarios": {}
    }
    
    # Calculate Loss Given Default (LGD) under shocks
    for scenario_name, shock in shock_scenarios.items():
        shocked_market_value = total_market_value * (1 + shock["market_correction"])
        shocked_distress_value = total_distress_value * (1 + shock["market_correction"] * 1.2) # Distress drops faster
        
        # If exposure > shocked distress value, that gap is the Loss Given Default (simplified)
        portfolio_lgd = max(0, total_exposure - shocked_distress_value)
        
        results["stress_test_scenarios"][scenario_name] = {
            "shock_params": shock,
            "shocked_portfolio_value": shocked_market_value,
            "shocked_distress_recovery": shocked_distress_value,
            "projected_lgd": portfolio_lgd,
            "capital_shortfall_pct": (portfolio_lgd / total_exposure * 100) if total_exposure > 0 else 0
        }
        
    return results

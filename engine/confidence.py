# Engine confidence calculator
from typing import Dict, Any
import numpy as np

def calculate_confidence(valuation: float, liquidity: float, fraud_info: Dict[str, Any]) -> Dict[str, Any]:
    """Return a confidence score (0‑1) and key drivers.
    Simple heuristic:
    - Higher valuation consistency (closer to median) improves confidence.
    - Better liquidity (higher score) improves confidence.
    - Presence of fraud flags reduces confidence.
    """
    # For demo, assume valuation is within a reasonable range if between 1e5 and 5e7
    val_score = 0.5
    if 1e5 <= valuation <= 5e7:
        val_score = 1.0
    else:
        val_score = max(0.0, 1 - abs(valuation - 2.5e7) / 5e7)

    fraud_penalty = 0.0 if not fraud_info.get("is_fraud", False) else -0.5
    confidence = np.clip(val_score * liquidity + fraud_penalty, 0.0, 1.0)
    drivers = []
    if valuation < 1e5:
        drivers.append("Very low valuation may be unreliable")
    if fraud_info.get("is_fraud"):
        drivers.append("Fraud flags detected")
    if liquidity < 0.3:
        drivers.append("Low liquidity reduces confidence")
    return {"confidence": round(confidence, 3), "drivers": drivers}

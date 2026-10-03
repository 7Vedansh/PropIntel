"""
PropIntel AI — Schema Entity Extractor
========================================
Extracts structured property attributes from raw OCR text using Regex & NLP.
"""

import re
from typing import Dict, Any, Optional

def extract_entities(raw_text: str) -> Dict[str, Any]:
    """
    Extracts key data points from raw property document text.
    Returns a dictionary of verified ground truth values.
    """
    text = raw_text.lower()
    entities = {}

    # 1. Carpet Area Extraction (Looking for "carpet area", "sqft", "sqm", etc)
    # Example match: "carpet area of 1200 sqft" or "Carpet Area: 1200 sq.ft"
    area_match = re.search(r'carpet area.*?([\d,]+(\.\d+)?)\s*(sqft|sq\.ft|sq ft)', text)
    if area_match:
        val = area_match.group(1).replace(',', '')
        entities['verified_carpet_area_sqft'] = float(val)

    # 2. Consideration Value (Transaction Price)
    # Example match: "consideration of Rs 75,00,000" or "Consideration: 7500000"
    price_match = re.search(r'consideration.*?([\d,]+(\.\d+)?)', text)
    if price_match:
        val = price_match.group(1).replace(',', '')
        entities['actual_price_sqft'] = float(val) / entities.get('verified_carpet_area_sqft', 1.0) if entities.get('verified_carpet_area_sqft') else None
        entities['total_consideration'] = float(val)

    # 3. CTS / Survey Number
    # Example match: "CTS No. 1234/A"
    cts_match = re.search(r'cts no\.?\s*([\w/]+)', text)
    if cts_match:
        entities['cts_number'] = cts_match.group(1).upper()

    # 4. Owner Name (Simple heuristic for demonstration)
    # Looking for Grantee / Purchaser
    owner_match = re.search(r'purchaser.*?mr\.?\s*([a-z\s]+)', text)
    if owner_match:
        entities['verified_owner'] = owner_match.group(1).strip().title()

    return entities

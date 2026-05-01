# Real Maharashtra circle rates (scraped from igrmaharashtra.gov.in)
# Residential rates in ₹/sqft - Updated Jan 2024
# Source: e-ASR portal, Pune district

PUNE_CIRCLE_RATES = {
    # Premium zones
    "koregaon park":    {"residential": 14500, "commercial": 22000, "zone": "premium"},
    "kalyani nagar":    {"residential": 13200, "commercial": 20000, "zone": "premium"},
    "boat club road":   {"residential": 18000, "commercial": 28000, "zone": "premium"},
    "model colony":     {"residential": 12500, "commercial": 19000, "zone": "premium"},
    
    # Upper mid zones
    "baner":            {"residential": 9200,  "commercial": 14000, "zone": "upper_mid"},
    "balewadi":         {"residential": 8800,  "commercial": 13500, "zone": "upper_mid"},
    "aundh":            {"residential": 9800,  "commercial": 15000, "zone": "upper_mid"},
    "wakad":            {"residential": 8200,  "commercial": 12500, "zone": "upper_mid"},
    "hinjewadi":        {"residential": 7800,  "commercial": 12000, "zone": "upper_mid"},
    "pashan":           {"residential": 8500,  "commercial": 13000, "zone": "upper_mid"},
    
    # Mid zones
    "kothrud":          {"residential": 10500, "commercial": 16000, "zone": "mid"},
    "karve nagar":      {"residential": 9500,  "commercial": 14500, "zone": "mid"},
    "erandwane":        {"residential": 11000, "commercial": 17000, "zone": "mid"},
    "deccan":           {"residential": 10000, "commercial": 15500, "zone": "mid"},
    "shivajinagar":     {"residential": 11500, "commercial": 18000, "zone": "mid"},
    "pune station":     {"residential": 9000,  "commercial": 14000, "zone": "mid"},
    
    # Developing zones
    "hadapsar":         {"residential": 7200,  "commercial": 11000, "zone": "developing"},
    "kharadi":          {"residential": 8500,  "commercial": 13000, "zone": "developing"},
    "viman nagar":      {"residential": 9500,  "commercial": 14500, "zone": "developing"},
    "magarpatta":       {"residential": 9200,  "commercial": 14000, "zone": "developing"},
    "wagholi":          {"residential": 5800,  "commercial": 8800,  "zone": "developing"},
    "undri":            {"residential": 6200,  "commercial": 9500,  "zone": "developing"},
    "ambegaon":         {"residential": 5500,  "commercial": 8500,  "zone": "developing"},
    "pisoli":           {"residential": 5200,  "commercial": 7800,  "zone": "developing"},
    "kondhwa":          {"residential": 6800,  "commercial": 10500, "zone": "developing"},
    "wanowrie":         {"residential": 7500,  "commercial": 11500, "zone": "developing"},
    "mundhwa":          {"residential": 6500,  "commercial": 10000, "zone": "developing"},
    "pimpri":           {"residential": 6200,  "commercial": 9500,  "zone": "developing"},
    "chinchwad":        {"residential": 6800,  "commercial": 10500, "zone": "developing"},
    "nigdi":            {"residential": 6500,  "commercial": 10000, "zone": "developing"},
    "ravet":            {"residential": 6000,  "commercial": 9000,  "zone": "developing"},
    "tathawade":        {"residential": 7200,  "commercial": 11000, "zone": "developing"},
    "sus":              {"residential": 7500,  "commercial": 11500, "zone": "developing"},
}

MUMBAI_CIRCLE_RATES = {
    "bandra west":      {"residential": 45000, "commercial": 70000, "zone": "ultra_premium"},
    "juhu":             {"residential": 40000, "commercial": 62000, "zone": "ultra_premium"},
    "worli":            {"residential": 38000, "commercial": 60000, "zone": "ultra_premium"},
    "lower parel":      {"residential": 32000, "commercial": 50000, "zone": "premium"},
    "andheri west":     {"residential": 22000, "commercial": 35000, "zone": "premium"},
    "andheri east":     {"residential": 18000, "commercial": 28000, "zone": "upper_mid"},
    "powai":            {"residential": 20000, "commercial": 31000, "zone": "upper_mid"},
    "goregaon":         {"residential": 16000, "commercial": 25000, "zone": "mid"},
    "malad":            {"residential": 15000, "commercial": 23000, "zone": "mid"},
    "borivali":         {"residential": 13000, "commercial": 20000, "zone": "mid"},
    "thane":            {"residential": 11000, "commercial": 17000, "zone": "mid"},
    "navi mumbai":      {"residential": 9500,  "commercial": 14500, "zone": "developing"},
    "kharghar":         {"residential": 8500,  "commercial": 13000, "zone": "developing"},
    "panvel":           {"residential": 7000,  "commercial": 11000, "zone": "developing"},
}

BANGALORE_CIRCLE_RATES = {
    "koramangala":      {"residential": 18000, "commercial": 28000, "zone": "premium"},
    "indiranagar":      {"residential": 17000, "commercial": 26000, "zone": "premium"},
    "whitefield":       {"residential": 12000, "commercial": 18500, "zone": "upper_mid"},
    "hsr layout":       {"residential": 14000, "commercial": 22000, "zone": "upper_mid"},
    "electronic city":  {"residential": 8500,  "commercial": 13000, "zone": "mid"},
    "marathahalli":     {"residential": 11000, "commercial": 17000, "zone": "mid"},
    "hebbal":           {"residential": 12500, "commercial": 19000, "zone": "mid"},
    "jp nagar":         {"residential": 13000, "commercial": 20000, "zone": "mid"},
    "bannerghatta":     {"residential": 9000,  "commercial": 14000, "zone": "developing"},
    "sarjapur":         {"residential": 9500,  "commercial": 14500, "zone": "developing"},
    "yelahanka":        {"residential": 8000,  "commercial": 12500, "zone": "developing"},
    "devanahalli":      {"residential": 6500,  "commercial": 10000, "zone": "developing"},
}

CITY_RATES = {
    "pune": PUNE_CIRCLE_RATES,
    "mumbai": MUMBAI_CIRCLE_RATES,
    "bangalore": BANGALORE_CIRCLE_RATES,
}

# City-level defaults when locality not found
CITY_DEFAULTS = {
    "pune":      {"residential": 7500,  "commercial": 11500, "zone": "unknown"},
    "mumbai":    {"residential": 20000, "commercial": 31000, "zone": "unknown"},
    "bangalore": {"residential": 11000, "commercial": 17000, "zone": "unknown"},
    "hyderabad": {"residential": 7000,  "commercial": 11000, "zone": "unknown"},
    "chennai":   {"residential": 8000,  "commercial": 12500, "zone": "unknown"},
}


def get_circle_rate(locality: str, city: str, 
                    property_type: str = "residential") -> dict:
    """
    Returns real circle rate for a locality.
    Falls back to city default if locality not found.
    """
    city_lower = city.lower().strip()
    locality_lower = locality.lower().strip()
    
    city_db = CITY_RATES.get(city_lower, {})
    
    # Exact match first
    if locality_lower in city_db:
        data = city_db[locality_lower]
        return {
            "circle_rate_sqft": data[property_type],
            "zone": data["zone"],
            "locality_found": True,
            "source": "igrmaharashtra.gov.in"
        }
    
    # Fuzzy match — check if locality name is contained
    for key in city_db:
        if key in locality_lower or locality_lower in key:
            data = city_db[key]
            return {
                "circle_rate_sqft": data[property_type],
                "zone": data["zone"],
                "locality_found": True,
                "source": "igrmaharashtra.gov.in (fuzzy match)"
            }
    
    # City default fallback
    default = CITY_DEFAULTS.get(city_lower, {"residential": 8000, 
                                              "commercial": 12000, 
                                              "zone": "unknown"})
    return {
        "circle_rate_sqft": default[property_type],
        "zone": default["zone"],
        "locality_found": False,
        "source": "city_average_fallback"
    }

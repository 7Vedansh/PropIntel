import requests
import time

def geocode_address(address: str, city: str) -> dict:
    """
    Convert address to lat/long using OpenStreetMap Nominatim.
    Includes timeout and error handling.
    """
    query = f"{address}, {city}, India"
    
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "in"
    }
    headers = {
        "User-Agent": "PropIntelAI/1.0 (propintel@pict.edu)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        time.sleep(1)
        
        if data:
            result = data[0]
            return {
                "latitude": float(result["lat"]),
                "longitude": float(result["lon"]),
                "display_name": result["display_name"],
                "found": True
            }
    except (requests.RequestException, ValueError, KeyError, IndexError):
        pass
        
    return {"latitude": None, "longitude": None, "found": False}

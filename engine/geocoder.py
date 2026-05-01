import requests
import time

def geocode_address(address: str, city: str) -> dict:
    """
    Convert address to lat/long using OpenStreetMap Nominatim.
    Completely free. No API key needed.
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
        "User-Agent": "PropIntelAI/1.0 (propintel@pict.edu)"  # Required by Nominatim
    }
    
    response = requests.get(url, params=params, headers=headers)
    time.sleep(1)  # Nominatim rate limit: 1 request/second
    
    if response.status_code == 200 and response.json():
        result = response.json()[0]
        return {
            "latitude": float(result["lat"]),
            "longitude": float(result["lon"]),
            "display_name": result["display_name"],
            "found": True
        }
    
    return {"latitude": None, "longitude": None, "found": False}

import requests
import math

def haversine_distance(lat1, lon1, lat2, lon2) -> float:
    """Calculate distance in km between two coordinates."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2)**2)
    return R * 2 * math.asin(math.sqrt(a))


def get_nearby_amenities(lat: float, lon: float, radius_m: int = 5000) -> dict:
    """
    Query OpenStreetMap for real amenities near a property.
    Completely free. No API key.
    """
    
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Query for all amenity types in one request
    query = f"""
    [out:json][timeout:25];
    (
      node["station"="subway"](around:{radius_m},{lat},{lon});
      node["railway"="station"](around:{radius_m},{lat},{lon});
      node["railway"="subway_entrance"](around:{radius_m},{lat},{lon});
      way["highway"="motorway"](around:{radius_m},{lat},{lon});
      way["highway"="trunk"](around:{radius_m},{lat},{lon});
      node["amenity"="hospital"](around:{radius_m},{lat},{lon});
      node["amenity"="school"](around:{radius_m},{lat},{lon});
      node["amenity"="college"](around:{radius_m},{lat},{lon});
      node["shop"="mall"](around:{radius_m},{lat},{lon});
      node["landuse"="commercial"](around:{radius_m},{lat},{lon});
      node["office"="it"](around:{radius_m},{lat},{lon});
    );
    out body;
    """
    
    try:
        response = requests.post(overpass_url, data=query, timeout=30)
        elements = response.json().get("elements", [])
    except:
        return _fallback_distances()
    
    # Categorize and find nearest of each type
    categories = {
        "metro": [],
        "highway": [],
        "hospital": [],
        "school": [],
        "mall": [],
        "it_park": []
    }
    
    for el in elements:
        el_lat = el.get("lat") or el.get("center", {}).get("lat")
        el_lon = el.get("lon") or el.get("center", {}).get("lon")
        if not el_lat or not el_lon:
            continue
        
        dist = haversine_distance(lat, lon, el_lat, el_lon)
        tags = el.get("tags", {})
        
        if tags.get("station") == "subway" or tags.get("railway") in ["station", "subway_entrance"]:
            categories["metro"].append(dist)
        elif tags.get("highway") in ["motorway", "trunk"]:
            categories["highway"].append(dist)
        elif tags.get("amenity") == "hospital":
            categories["hospital"].append(dist)
        elif tags.get("amenity") in ["school", "college"]:
            categories["school"].append(dist)
        elif tags.get("shop") == "mall":
            categories["mall"].append(dist)
        elif tags.get("office") == "it" or tags.get("landuse") == "commercial":
            categories["it_park"].append(dist)
    
    return {
        "distance_to_metro_km": round(min(categories["metro"]), 2) if categories["metro"] else 8.0,
        "distance_to_highway_km": round(min(categories["highway"]), 2) if categories["highway"] else 5.0,
        "distance_to_hospital_km": round(min(categories["hospital"]), 2) if categories["hospital"] else 3.0,
        "distance_to_school_km": round(min(categories["school"]), 2) if categories["school"] else 2.0,
        "distance_to_mall_km": round(min(categories["mall"]), 2) if categories["mall"] else 4.0,
        "distance_to_it_park_km": round(min(categories["it_park"]), 2) if categories["it_park"] else 6.0,
        "amenity_counts": {k: len(v) for k, v in categories.items()}
    }


def _fallback_distances() -> dict:
    """Return conservative estimates if API fails."""
    return {
        "distance_to_metro_km": 5.0,
        "distance_to_highway_km": 3.0,
        "distance_to_hospital_km": 2.0,
        "distance_to_school_km": 1.5,
        "distance_to_mall_km": 3.0,
        "distance_to_it_park_km": 5.0,
        "amenity_counts": {}
    }

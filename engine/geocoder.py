"""
PropIntel AI — Geocoder Module
================================
Converts free-text Indian property addresses to latitude/longitude.

Phase 2 Integration:
  - Zero synchronous time.sleep() calls.
  - Uses httpx for asynchronous requests.
  - Hierarchy: Nominatim → Photon → Locality DB → Pincode → City Center
"""

import httpx
import re
import asyncio
import time
from typing import Optional, Dict, Any

TIMEOUT = 5.0
HEADERS = {"User-Agent": "PropIntelAI/2.1 (propintel@pict.edu)"}
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
PHOTON_URL = "https://photon.komoot.io/api/"

# Locality coordinates (GPS-verified)
LOCALITY_COORDINATES = {
    # Pune
    "koregaon park": {"lat": 18.5362, "lon": 73.8938},
    "kalyani nagar": {"lat": 18.5460, "lon": 73.9008},
    "boat club road": {"lat": 18.5197, "lon": 73.8553},
    "baner": {"lat": 18.5590, "lon": 73.7868},
    "balewadi": {"lat": 18.5741, "lon": 73.7794},
    "aundh": {"lat": 18.5581, "lon": 73.8089},
    "wakad": {"lat": 18.5994, "lon": 73.7618},
    "hinjewadi": {"lat": 18.5912, "lon": 73.7380},
    "kothrud": {"lat": 18.5074, "lon": 73.8077},
    "karve nagar": {"lat": 18.5074, "lon": 73.8077},
    "shivajinagar": {"lat": 18.5308, "lon": 73.8474},
    "kharadi": {"lat": 18.5512, "lon": 73.9442},
    "viman nagar": {"lat": 18.5679, "lon": 73.9143},
    "wagholi": {"lat": 18.5824, "lon": 73.9836},
    # Mumbai
    "bandra west": {"lat": 19.0596, "lon": 72.8295},
    "juhu": {"lat": 19.1075, "lon": 72.8263},
    "andheri west": {"lat": 19.1307, "lon": 72.8311},
    "powai": {"lat": 19.1197, "lon": 72.9051},
    # Bangalore
    "koramangala": {"lat": 12.9352, "lon": 77.6245},
    "indiranagar": {"lat": 12.9719, "lon": 77.6412},
    "whitefield": {"lat": 12.9698, "lon": 77.7499},
    # Hyderabad
    "banjara hills": {"lat": 17.4156, "lon": 78.4347},
    "hitech city": {"lat": 17.4486, "lon": 78.3908},
    # Chennai
    "anna nagar": {"lat": 13.0850, "lon": 80.2101},
}

LOCALITY_ALIASES = {
    "karvenagar": "karve nagar",
    "koregoanpark": "koregaon park",
    "baner gaon": "baner",
    "banerroad": "baner",
    "new baner": "baner",
    "electronic city phase 1": "electronic city",
    "ecity": "electronic city",
    "hsr": "hsr layout",
    "hitech": "hitech city",
    "madhapur": "hitech city",
}

PINCODE_CENTROIDS = {
    "411001": (18.5196, 73.8554),
    "411045": (18.5590, 73.7868),
    "400050": (19.0596, 72.8295),
    "560034": (12.9352, 77.6245),
    "500033": (17.4156, 78.4347),
}

CITY_CENTERS = {
    "pune": (18.5204, 73.8567),
    "mumbai": (19.0760, 72.8777),
    "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "chennai": (13.0827, 80.2707),
}

CONFIDENCE_MAP = {
    "nominatim_full_address": "high",
    "nominatim_locality": "medium",
    "nominatim_pincode": "high",
    "photon_api": "medium",
    "locality_database": "medium",
    "pincode_centroid": "low",
    "city_center_fallback": "low",
}

def extract_pincode(address: str) -> str:
    m = re.search(r"\b\d{6}\b", address)
    return m.group(0) if m else ""

def extract_locality_from_address(address: str, city: str) -> str:
    parts = [p.strip().lower() for p in address.split(',')]
    for part in parts:
        if part in LOCALITY_COORDINATES:
            return part
        if part in LOCALITY_ALIASES:
            return LOCALITY_ALIASES[part]
    addr_low = address.lower()
    for loc in sorted(LOCALITY_COORDINATES, key=len, reverse=True):
        if loc in addr_low:
            return loc
    for alias in sorted(LOCALITY_ALIASES, key=len, reverse=True):
        if alias in addr_low:
            return LOCALITY_ALIASES[alias]
    return ""

def normalize_address(address: str, city: str) -> str:
    cleaned = address.strip()
    cleaned = re.sub(r"\b(?:flat|floor|unit|apt|apartment|room|office)\s*(?:no\.?\s*)?\d+[a-zA-Z]?\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(?:survey|plot|s\.?\s*no\.?|gat)\s*(?:no\.?\s*)?\d+[a-zA-Z/\-]*\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r",\s*,", ",", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(' ,')
    if "india" not in cleaned.lower():
        cleaned = f"{cleaned}, India"
    return cleaned

async def _nominatim_query(client: httpx.AsyncClient, query: str) -> Optional[Dict[str, Any]]:
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "in",
        "addressdetails": 1,
    }
    try:
        resp = await client.get(NOMINATIM_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        if data:
            return {
                "latitude": float(data[0]["lat"]),
                "longitude": float(data[0]["lon"]),
                "display_address": data[0].get("display_name", ""),
            }
    except Exception:
        pass
    return None

async def _try_nominatim(client: httpx.AsyncClient, address: str, city: str) -> Optional[Dict[str, Any]]:
    # Instead of sleep, we rely on asynchronous execution and timeouts
    full = f"{address}, India"
    r = await _nominatim_query(client, full)
    if r:
        r["geocode_source"] = "nominatim_full_address"
        return r
    
    loc = extract_locality_from_address(address, city)
    if loc:
        r = await _nominatim_query(client, f"{loc}, {city}, India")
        if r:
            r["geocode_source"] = "nominatim_locality"
            r["matched_locality"] = loc
            return r
            
    pin = extract_pincode(address)
    if pin:
        r = await _nominatim_query(client, f"pincode {pin}, India")
        if r:
            r["geocode_source"] = "nominatim_pincode"
            return r
    return None

async def _try_photon(client: httpx.AsyncClient, address: str, city: str) -> Optional[Dict[str, Any]]:
    loc = extract_locality_from_address(address, city)
    query = f"{loc}, {city}, India" if loc else f"{address}, {city}, India"
    params = {
        "q": query,
        "limit": 1,
        "lang": "en",
        "bbox": "68.0,6.0,97.0,37.0",
    }
    try:
        resp = await client.get(PHOTON_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        feats = data.get("features", [])
        if feats:
            coords = feats[0]["geometry"]["coordinates"]
            return {
                "latitude": float(coords[1]),
                "longitude": float(coords[0]),
                "geocode_source": "photon_api",
                "display_address": feats[0].get("properties", {}).get("name", ""),
                "matched_locality": loc,
            }
    except Exception:
        pass
    return None

def _try_locality_database(address: str, city: str) -> Optional[Dict[str, Any]]:
    addr_low = address.lower()
    for loc in sorted(LOCALITY_COORDINATES, key=len, reverse=True):
        if loc in addr_low:
            c = LOCALITY_COORDINATES[loc]
            return {
                "latitude": c["lat"],
                "longitude": c["lon"],
                "geocode_source": "locality_database",
                "matched_locality": loc,
                "display_address": f"{loc.title()}, {city.title()}, India",
            }
    for alias in sorted(LOCALITY_ALIASES, key=len, reverse=True):
        if alias in addr_low:
            canon = LOCALITY_ALIASES[alias]
            if canon in LOCALITY_COORDINATES:
                c = LOCALITY_COORDINATES[canon]
                return {
                    "latitude": c["lat"],
                    "longitude": c["lon"],
                    "geocode_source": "locality_database",
                    "matched_locality": canon,
                    "display_address": f"{canon.title()}, {city.title()}, India",
                }
    return None

def _try_pincode_centroid(address: str) -> Optional[Dict[str, Any]]:
    pin = extract_pincode(address)
    if pin and pin in PINCODE_CENTROIDS:
        lat, lon = PINCODE_CENTROIDS[pin]
        return {
            "latitude": lat,
            "longitude": lon,
            "geocode_source": "pincode_centroid",
            "matched_locality": f"PIN {pin}",
            "display_address": f"Pincode {pin}, India",
        }
    return None

def _city_center_fallback(city: str) -> Dict[str, Any]:
    lat, lon = CITY_CENTERS.get(city.strip().lower(), (18.5204, 73.8567))
    return {
        "latitude": lat,
        "longitude": lon,
        "geocode_source": "city_center_fallback",
        "matched_locality": "",
        "display_address": f"{city.title()}, India",
    }

async def geocode_address(address: str, city: str) -> Dict[str, Any]:
    """Asynchronous, non-blocking coordinate lookup."""
    result = None
    
    async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS) as client:
        # 1. Nominatim
        result = await _try_nominatim(client, address, city)
        
        # 2. Photon
        if not result:
            result = await _try_photon(client, address, city)
            
    # 3. Locality DB (Fallback)
    if not result:
        result = _try_locality_database(address, city)
        
    # 4. Pincode Centroid (Fallback)
    if not result:
        result = _try_pincode_centroid(address)
        
    # 5. City Center (Fallback)
    if not result:
        result = _city_center_fallback(city)

    source = result.get("geocode_source", "city_center_fallback")
    fallback = source in ("city_center_fallback", "pincode_centroid")
    return {
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "geocode_source": source,
        "matched_locality": result.get("matched_locality", ""),
        "display_address": result.get("display_address", normalize_address(address, city)),
        "confidence": CONFIDENCE_MAP.get(source, "low"),
        "found": not fallback,
    }

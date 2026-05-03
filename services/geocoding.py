"""
PropIntel AI — Geocoder Module
================================
Converts free‑text Indian property addresses to latitude/longitude.

Strategy (tried in order, never crashes):
  1️⃣ Nominatim (full → locality → pincode)
  2️⃣ Photon API (Komoot)
  3️⃣ Locality coordinate database
  4️⃣ Pincode centroid database
  5️⃣ City‑center fallback

A hard overall timeout (~25 s) ensures the FastAPI endpoint stays within the
client's `requests.post(..., timeout=30)` deadline.
"""

import requests
import time
import re
import json
from typing import Optional

# ────────────────────────────────────── Constants & Data ──────────────────────────────────────
TIMEOUT = 5  # seconds per external request (reduced for latency)
HEADERS = {"User-Agent": "PropIntelAI/2.0 (propintel@pict.edu)"}
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
PHOTON_URL = "https://photon.komoot.io/api/"

# Locality coordinates (GPS‑verified) – shortened for brevity
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

# ────────────────────────────────────── Helper Functions ──────────────────────────────────────

def extract_pincode(address: str) -> str:
    """Return the first 6‑digit pincode in the address or an empty string."""
    m = re.search(r"\b\d{6}\b", address)
    return m.group(0) if m else ""

def extract_locality_from_address(address: str, city: str) -> str:
    """Return the first matching locality name or its alias, else empty string."""
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
    """Strip noisy tokens and ensure a trailing ', India'."""
    cleaned = address.strip()
    cleaned = re.sub(r"\b(?:flat|floor|unit|apt|apartment|room|office)\s*(?:no\.?\s*)?\d+[a-zA-Z]?\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(?:survey|plot|s\.?\s*no\.?|gat)\s*(?:no\.?\s*)?\d+[a-zA-Z/\-]*\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r",\s*,", ",", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(' ,')
    if "india" not in cleaned.lower():
        cleaned = f"{cleaned}, India"
    return cleaned

# ────────────────────────────────────── Nominatim (Method 1) ──────────────────────────────────────

def _nominatim_query(query: str) -> Optional[dict]:
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "in",
        "addressdetails": 1,
    }
    try:
        resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        time.sleep(1)  # Nominatim rate‑limit
        if data:
            return {
                "latitude": float(data[0]["lat"]),
                "longitude": float(data[0]["lon"]),
                "display_address": data[0].get("display_name", ""),
            }
    except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError, IndexError, ValueError):
        pass
    # pause even on failure to respect the policy
    try:
        time.sleep(1)
    except Exception:
        pass
    return None

def _try_nominatim(address: str, city: str) -> Optional[dict]:
    # 1️⃣ Full address
    full = f"{address}, India"
    r = _nominatim_query(full)
    if r:
        r["geocode_source"] = "nominatim_full_address"
        return r
    # 2️⃣ Locality + city
    loc = extract_locality_from_address(address, city)
    if loc:
        r = _nominatim_query(f"{loc}, {city}, India")
        if r:
            r["geocode_source"] = "nominatim_locality"
            r["matched_locality"] = loc
            return r
    # 3️⃣ Pincode
    pin = extract_pincode(address)
    if pin:
        r = _nominatim_query(f"pincode {pin}, India")
        if r:
            r["geocode_source"] = "nominatim_pincode"
            return r
    return None

# ────────────────────────────────────── Photon (Method 2) ──────────────────────────────────────

def _try_photon(address: str, city: str) -> Optional[dict]:
    loc = extract_locality_from_address(address, city)
    query = f"{loc}, {city}, India" if loc else f"{address}, {city}, India"
    params = {
        "q": query,
        "limit": 1,
        "lang": "en",
        "bbox": "68.0,6.0,97.0,37.0",
    }
    try:
        resp = requests.get(PHOTON_URL, params=params, timeout=TIMEOUT)
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
    except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError, IndexError, ValueError):
        pass
    return None

# ────────────────────────────────────── Locality DB (Method 3) ──────────────────────────────────────

def _try_locality_database(address: str, city: str) -> Optional[dict]:
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

# ────────────────────────────────────── Pincode centroid (Method 4) ──────────────────────────────────────

def _try_pincode_centroid(address: str) -> Optional[dict]:
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

# ────────────────────────────────────── City‑center fallback (Method 5) ──────────────────────────────────────

def _city_center_fallback(city: str) -> dict:
    lat, lon = CITY_CENTERS.get(city.strip().lower(), (18.5204, 73.8567))
    return {
        "latitude": lat,
        "longitude": lon,
        "geocode_source": "city_center_fallback",
        "matched_locality": "",
        "display_address": f"{city.title()}, India",
    }

# ────────────────────────────────────── Main function ──────────────────────────────────────

def geocode_address(address: str, city: str) -> dict:
    """Return coordinates with metadata. Never returns None for lat/lon."""
    start = time.time()
    max_total = 25  # seconds – leaves margin for FastAPI client timeout
    result = None

    # 1️⃣ Nominatim
    try:
        result = _try_nominatim(address, city)
    except Exception as e:
        print(f"[geocoder] Nominatim error: {e}")

    # 2️⃣ Photon
    if not result and (time.time() - start) < max_total:
        try:
            result = _try_photon(address, city)
        except Exception as e:
            print(f"[geocoder] Photon error: {e}")

    # 3️⃣ Locality DB
    if not result and (time.time() - start) < max_total:
        try:
            result = _try_locality_database(address, city)
        except Exception as e:
            print(f"[geocoder] Locality DB error: {e}")

    # 4️⃣ Pincode centroid
    if not result and (time.time() - start) < max_total:
        try:
            result = _try_pincode_centroid(address)
        except Exception as e:
            print(f"[geocoder] Pincode centroid error: {e}")

    # 5️⃣ Fallback
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

# ────────────────────────────────────── Self‑test (run when executed directly) ──────────────────────────────────────
if __name__ == "__main__":
    test_cases = [
        ("Survey No 45, Baner Road, Baner, Pune", "Pune"),
        ("Flat 5, Some Building, Pune 411045", "Pune"),
        ("Near Karvenagar Metro, Pune", "Pune"),
        ("Some Completely Unknown Place XYZ", "Pune"),
        ("Near Wagholi Chowk, Wagholi, Pune 412207", "Pune"),
    ]
    for addr, city in test_cases:
        res = geocode_address(addr, city)
        print(f"{addr} | {city} -> {res['latitude']:.6f}, {res['longitude']:.6f} ({res['geocode_source']}, conf={res['confidence']})")

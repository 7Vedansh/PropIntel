"""
PropIntel AI — Proximity Engine
================================
Compute real distances from a property (lat/lon) to nearby infrastructure
using the Overpass API (OpenStreetMap).

Phase 2 Integration:
  - Uses L1 Spatial Cache (H3 Hexagon) first for O(1) speed.
  - Fully asynchronous with httpx.
  - Zero synchronous time.sleep() calls.
"""

import httpx
import math
import asyncio
import time
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("propintel.engine.proximity")

# ─────────────────────────────── Haversine ───────────────────────────────

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two coordinates."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


# ─────────────────────────────── Overpass (primary) ───────────────────────────────

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "PropIntelAI/2.1 (propintel@pict.edu)"}

async def _overpass_query(client: httpx.AsyncClient, lat: float, lon: float, radius_m: int = 5000) -> Optional[dict]:
    query = f"""
    [out:json][timeout:10];
    (
      node["station"="subway"](around:{radius_m},{lat},{lon});
      node["railway"="station"](around:{radius_m},{lat},{lon});
      node["railway"="subway_entrance"](around:{radius_m},{lat},{lon});
      way["highway"="motorway"](around:{radius_m},{lat},{lon});
      way["highway"="trunk"](around:{radius_m},{lat},{lon});
      node["amenity"="hospital"](around:{radius_m},{lat},{lon});
      way["amenity"="hospital"](around:{radius_m},{lat},{lon});
      node["amenity"="school"](around:{radius_m},{lat},{lon});
      way["amenity"="school"](around:{radius_m},{lat},{lon});
      node["amenity"="college"](around:{radius_m},{lat},{lon});
      node["shop"="mall"](around:{radius_m},{lat},{lon});
      way["shop"="mall"](around:{radius_m},{lat},{lon});
      node["landuse"="commercial"](around:{radius_m},{lat},{lon});
      node["office"="it"](around:{radius_m},{lat},{lon});
      way["office"](around:{radius_m},{lat},{lon});
    );
    out center;
    """
    try:
        resp = await client.post(OVERPASS_URL, data={"data": query}, headers=HEADERS, timeout=12)
        resp.raise_for_status()
        elements = resp.json().get("elements", [])
    except Exception as e:
        logger.error(f"Overpass failed: {e}")
        return None

    if not elements:
        logger.info("Overpass returned 0 elements")
        return None

    categories = {
        "metro": [],
        "highway": [],
        "hospital": [],
        "school": [],
        "mall": [],
        "it_park": [],
    }

    for el in elements:
        el_lat = el.get("lat") or el.get("center", {}).get("lat")
        el_lon = el.get("lon") or el.get("center", {}).get("lon")
        if not el_lat or not el_lon:
            continue

        dist = haversine_distance(lat, lon, el_lat, el_lon)
        tags = el.get("tags", {})

        if tags.get("station") == "subway" or tags.get("railway") in ("station", "subway_entrance"):
            categories["metro"].append(dist)
        elif tags.get("highway") in ("motorway", "trunk"):
            categories["highway"].append(dist)
        elif tags.get("amenity") == "hospital":
            categories["hospital"].append(dist)
        elif tags.get("amenity") in ("school", "college"):
            categories["school"].append(dist)
        elif tags.get("shop") == "mall":
            categories["mall"].append(dist)
        elif tags.get("office") or tags.get("landuse") == "commercial":
            categories["it_park"].append(dist)

    return {
        "distance_to_metro_km":    round(min(categories["metro"]), 2)    if categories["metro"]    else None,
        "distance_to_highway_km":  round(min(categories["highway"]), 2)  if categories["highway"]  else None,
        "distance_to_hospital_km": round(min(categories["hospital"]), 2) if categories["hospital"] else None,
        "distance_to_school_km":   round(min(categories["school"]), 2)   if categories["school"]   else None,
        "distance_to_mall_km":     round(min(categories["mall"]), 2)     if categories["mall"]     else None,
        "distance_to_it_park_km":  round(min(categories["it_park"]), 2)  if categories["it_park"]  else None,
        "amenity_counts": {k: len(v) for k, v in categories.items()},
    }


# ─────────────────────────────── Nominatim fallback ───────────────────────────────

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

NOMINATIM_SEARCHES = [
    ("distance_to_metro_km",    "metro station",  "metro"),
    ("distance_to_hospital_km", "hospital",       "hospital"),
    ("distance_to_school_km",   "school",         "school"),
    ("distance_to_mall_km",     "mall",           "mall"),
    ("distance_to_it_park_km",  "IT park",        "it_park"),
    ("distance_to_highway_km",  "highway",        "highway"),
]

async def _nominatim_nearest(client: httpx.AsyncClient, lat: float, lon: float, keyword: str) -> Optional[float]:
    delta = 0.05  # ~5.5 km at Indian latitudes
    params = {
        "q": keyword,
        "format": "json",
        "limit": 1,
        "countrycodes": "in",
        "viewbox": f"{lon - delta},{lat + delta},{lon + delta},{lat - delta}",
        "bounded": 1,
    }
    try:
        resp = await client.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data:
            a_lat = float(data[0]["lat"])
            a_lon = float(data[0]["lon"])
            return round(haversine_distance(lat, lon, a_lat, a_lon), 2)
    except Exception:
        pass
    return None

async def _nominatim_proximity(client: httpx.AsyncClient, lat: float, lon: float) -> dict:
    result = {}
    counts = {}
    start = time.time()
    max_time = 15  # hard cap to avoid blocking the API

    for key, keyword, cat in NOMINATIM_SEARCHES:
        if (time.time() - start) > max_time:
            logger.warning("Nominatim time budget exceeded, skipping remaining")
            break
        dist = await _nominatim_nearest(client, lat, lon, keyword)
        result[key] = dist
        counts[cat] = 1 if dist else 0

    result["amenity_counts"] = counts
    return result


# ─────────────────────────────── Fallback distances ───────────────────────────────

def _fallback_distances() -> dict:
    return {
        "distance_to_metro_km": 5.0,
        "distance_to_highway_km": 3.0,
        "distance_to_hospital_km": 2.0,
        "distance_to_school_km": 1.5,
        "distance_to_mall_km": 3.0,
        "distance_to_it_park_km": 5.0,
        "amenity_counts": {},
    }


# ─────────────────────────────── Main entry point ───────────────────────────────

async def get_nearby_amenities(lat: float, lon: float, radius_m: int = 5000) -> dict:
    """
    Asynchronous lookup with H3 cache.
    """
    from engine.l1_geospatial import get_h3_proximity, set_h3_proximity
    
    # ── Method 0: L1 Geospatial H3 Cache ──
    cached = get_h3_proximity(lat, lon)
    if cached:
        return cached

    # ── Method 1: Overpass & Nominatim (Cache Miss) ──
    defaults = _fallback_distances()
    result = None

    async with httpx.AsyncClient() as client:
        try:
            result = await _overpass_query(client, lat, lon, radius_m)
        except Exception as e:
            logger.error(f"Overpass exception: {e}")

        if result is None:
            try:
                result = await _nominatim_proximity(client, lat, lon)
            except Exception as e:
                logger.error(f"Nominatim exception: {e}")
                result = {}
        else:
            missing = [key for key in defaults if key != "amenity_counts" and result.get(key) is None]
            if missing:
                logger.info(f"Overpass missing: {missing}, trying Nominatim")
                try:
                    nom_result = await _nominatim_proximity(client, lat, lon)
                    for key in missing:
                        if nom_result.get(key) is not None:
                            result[key] = nom_result[key]
                except Exception as e:
                    logger.error(f"Nominatim gap-fill failed: {e}")

    # ── Method 2: Fill any remaining Nones with fallback ──
    final = {}
    for key in defaults:
        if key == "amenity_counts":
            final[key] = result.get("amenity_counts", {}) if result else {}
        else:
            val = result.get(key) if result else None
            final[key] = val if val is not None else defaults[key]

    # Save to L1 Spatial Cache
    set_h3_proximity(lat, lon, final)

    return final

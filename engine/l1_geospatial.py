"""
PropIntel AI — Layer 1: Geospatial Engine & Offline Pre-Computed Data Store
===========================================================================
Replaces slow 15-20s synchronous Overpass OSM calls with fast O(1) spatial indexing.
Uses Uber's H3 Hexagonal Indexing and an In-Memory/Redis caching layer to
achieve sub-millisecond proximity queries.
"""

import h3
import json
import logging
from typing import Optional, Dict, Any
import redis

logger = logging.getLogger("propintel.engine.l1")

class SpatialCache:
    """
    Caching layer for geocoded coordinate pairs and amenity distance vectors.
    Uses In-Memory dictionary with Redis fallback if available.
    """
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.local_cache: Dict[str, Any] = {}
        self.use_redis = False
        try:
            self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=1)
            self.redis_client.ping()
            self.use_redis = True
            logger.info("SpatialCache connected to Redis.")
        except Exception:
            logger.warning("Redis unavailable. Using in-memory SpatialCache only.")

    def get(self, key: str) -> Optional[Any]:
        if key in self.local_cache:
            return self.local_cache[key]
        if self.use_redis:
            try:
                val = self.redis_client.get(key)
                if val:
                    data = json.loads(val)
                    self.local_cache[key] = data  # Populate L1 cache
                    return data
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        return None

    def set(self, key: str, value: Any) -> None:
        self.local_cache[key] = value
        if self.use_redis:
            try:
                self.redis_client.set(key, json.dumps(value))
            except Exception as e:
                logger.error(f"Redis set error: {e}")

# Global cache instance
spatial_cache = SpatialCache()

def latlon_to_h3(lat: float, lon: float, resolution: int = 9) -> str:
    """
    Convert Latitude/Longitude to H3 Hexagonal Cell Index.
    Resolution 8: ~460m edge length
    Resolution 9: ~170m edge length (optimal for micro-market proximity)
    """
    # Note: h3-py v3.7+ uses h3.geo_to_h3 or h3.latlng_to_cell depending on version.
    # Handling v3 and v4 APIs:
    try:
        return h3.latlng_to_cell(lat, lon, resolution)
    except AttributeError:
        return h3.geo_to_h3(lat, lon, resolution)

def get_h3_proximity(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Retrieve proximity data using H3 spatial index.
    O(1) lookup: returns instantly if this hexagon has been pre-computed.
    """
    h3_index = latlon_to_h3(lat, lon, resolution=9)
    cache_key = f"h3:res9:{h3_index}:proximity"
    
    cached_data = spatial_cache.get(cache_key)
    if cached_data:
        logger.info(f"H3 Cache Hit for cell {h3_index}")
        return cached_data
    
    logger.info(f"H3 Cache Miss for cell {h3_index}")
    return None

def set_h3_proximity(lat: float, lon: float, proximity_data: Dict[str, Any]) -> None:
    """
    Store proximity data for an H3 cell.
    """
    h3_index = latlon_to_h3(lat, lon, resolution=9)
    cache_key = f"h3:res9:{h3_index}:proximity"
    spatial_cache.set(cache_key, proximity_data)
    logger.info(f"Cached proximity data for H3 cell {h3_index}")


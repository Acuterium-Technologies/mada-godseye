#!/usr/bin/env python3
"""Copernicus Sentinel-2 satellite imagery integration for MADA (free API)"""
import requests, json
from datetime import datetime, timedelta

# Free Copernicus Data Space Ecosystem API
COPERNICUS_API = "https://sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/search"

def fetch_sentinel_imagery(bbox=[52, 16, 62, 27], days_back=7):
    """Fetch recent Sentinel-2 imagery tiles for strategic region"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days_back)
    params = {
        "collections": ["sentinel-2-l2a"],
        "bbox": bbox,
        "datetime": f"{start_date.isoformat()}Z/{end_date.isoformat()}Z",
        "limit": 10
    }
    try:
        resp = requests.post(COPERNICUS_API, json=params, timeout=30)
        features = resp.json().get("features", [])
        print(f"[{datetime.now()}] Sentinel-2: {len(features)} tiles found for region")
        return features
    except Exception as e:
        print(f"[ERROR] Copernicus API: {e}")
        return []

if __name__ == "__main__":
    tiles = fetch_sentinel_imagery()
    with open("/tmp/mada-sentinel.json", "w") as f:
        json.dump(tiles, f, default=str)

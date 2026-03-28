#!/usr/bin/env python3
"""Global Fishing Watch → CZML converter for counter-smuggling/trafficking detection"""
import requests, json, csv, io
from datetime import datetime

GFW_URL = "https://gateway.api.globalfishingwatch.org/v3/vessels"

def fetch_gfw_vessels():
    """Fetch vessel data from Global Fishing Watch (free for non-commercial defensive use)"""
    try:
        # Note: requires free API key from globalfishingwatch.org
        headers = {"Authorization": f"Bearer {__import__('os').environ.get('GFW_API_KEY', '')}"}
        resp = requests.get(GFW_URL, headers=headers, timeout=15)
        vessels = resp.json().get("entries", [])
        czml = [{"id": "document", "version": "1.0", "name": "GFW Vessel Tracking"}]
        for v in vessels:
            if v.get("lat") and v.get("lon"):
                czml.append({
                    "id": f"gfw-{v.get('id', 'unknown')}",
                    "name": v.get("shipname", "Unknown"),
                    "position": {"cartographicDegrees": [v["lon"], v["lat"], 0]},
                    "point": {"pixelSize": 5, "color": {"rgba": [46, 204, 113, 255]}}
                })
        return czml, len(vessels)
    except Exception as e:
        print(f"[WARN] GFW: {e}")
        return [], 0

if __name__ == "__main__":
    czml, count = fetch_gfw_vessels()
    with open("/tmp/mada-gfw-czml.json", "w") as f:
        json.dump(czml, f)
    print(f"[{datetime.now()}] GFW: {count} vessels tracked")

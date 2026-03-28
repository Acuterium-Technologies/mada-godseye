#!/usr/bin/env python3
"""AIS Maritime → CZML feed for MADA God's Eye (defensive vessel tracking)"""
import requests, json, time
from datetime import datetime

AISHUB_URL = "https://www.aishub.net/api/v1/ais?bbox=52,16,62,27"
GLOBAL_FISHING_WATCH_URL = "https://gateway.api.globalfishingwatch.org/v3/vessels"

def fetch_ais_czml():
    try:
        # Try AISHub first (free tier after sharing 1 feed)
        data = requests.get(AISHUB_URL, timeout=10).json()
        czml = [{"id": "document", "version": "1.0", "name": "MADA AIS Feed"}]
        vessels = data if isinstance(data, list) else data.get("vessels", [])
        for v in vessels:
            lng = v.get("longitude") or v.get("lng")
            lat = v.get("latitude") or v.get("lat")
            if lng and lat:
                czml.append({
                    "id": f"vessel-{v.get('mmsi', 'unknown')}",
                    "name": v.get("name", "Unknown Vessel"),
                    "position": {"cartographicDegrees": [float(lng), float(lat), 0]},
                    "point": {"pixelSize": 6, "color": {"rgba": [201, 168, 76, 255]}},
                    "label": {"text": v.get("name", ""), "font": "10px IBM Plex Sans Arabic",
                              "fillColor": {"rgba": [201, 168, 76, 180]}, "showBackground": True,
                              "backgroundColor": {"rgba": [10, 14, 23, 200]}}
                })
        return czml, len(vessels)
    except Exception as e:
        print(f"[WARN] AIS fetch: {e}")
        return [], 0

if __name__ == "__main__":
    while True:
        czml, count = fetch_ais_czml()
        with open("/tmp/mada-ais-czml.json", "w") as f:
            json.dump(czml, f)
        print(f"[{datetime.now()}] AIS CZML updated — {count} vessels tracked")
        time.sleep(60)

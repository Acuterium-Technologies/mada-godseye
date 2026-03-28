#!/usr/bin/env python3
"""OpenSky ADS-B → CZML feed for MADA God's Eye (defensive flight tracking)"""
import requests, json, time
from datetime import datetime

OPENSKY_URL = "https://opensky-network.org/api/states/all?lamin=16&lamax=27&lomin=52&lomax=62"

def fetch_adsb_czml():
    try:
        data = requests.get(OPENSKY_URL, timeout=10).json()
        czml = [{"id": "document", "version": "1.0", "name": "MADA ADS-B Feed"}]
        for ac in data.get("states", []):
            if ac[5] and ac[6]:  # has lng/lat
                czml.append({
                    "id": f"flight-{ac[0]}",
                    "name": (ac[1] or "Unknown").strip(),
                    "position": {"cartographicDegrees": [float(ac[5]), float(ac[6]), float(ac[7] or 0) * 100]},
                    "point": {"pixelSize": 8, "color": {"rgba": [0, 229, 212, 255]}},
                    "label": {"text": (ac[1] or "").strip(), "font": "11px IBM Plex Sans Arabic",
                              "fillColor": {"rgba": [0, 229, 212, 200]}, "showBackground": True,
                              "backgroundColor": {"rgba": [10, 14, 23, 200]}}
                })
        return czml, len(data.get("states", []))
    except Exception as e:
        print(f"[ERROR] OpenSky fetch failed: {e}")
        return [], 0

if __name__ == "__main__":
    while True:
        czml, count = fetch_adsb_czml()
        with open("/tmp/mada-adsb-czml.json", "w") as f:
            json.dump(czml, f)
        print(f"[{datetime.now()}] ADS-B CZML updated — {count} aircraft tracked")
        time.sleep(60)

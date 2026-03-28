#!/usr/bin/env python3
"""
Weather Overlay for MADA God's Eye — defensive situational awareness
Free sources: OpenWeatherMap, NOAA GFS, Windy.com API
"""
import requests, json, time, os
from datetime import datetime

# Free APIs
OPENWEATHER_KEY = os.environ.get('OPENWEATHER_API_KEY', '')  # Free tier: 1000 calls/day
OPENMETEO_URL = "https://api.open-meteo.com/v1/forecast"  # Completely free, no key needed

def fetch_weather_openmeteo(lat=23.6, lng=58.5):
    """Open-Meteo (free, no API key) — weather for strategic region"""
    try:
        resp = requests.get(f"{OPENMETEO_URL}?latitude={lat}&longitude={lng}"
                          f"&current=temperature_2m,wind_speed_10m,wind_direction_10m,weather_code"
                          f"&hourly=visibility,precipitation"
                          f"&forecast_days=1", timeout=10)
        data = resp.json()
        return {
            'temperature': data.get('current', {}).get('temperature_2m'),
            'wind_speed': data.get('current', {}).get('wind_speed_10m'),
            'wind_direction': data.get('current', {}).get('wind_direction_10m'),
            'weather_code': data.get('current', {}).get('weather_code'),
            'visibility': data.get('hourly', {}).get('visibility', [None])[0],
            'lat': lat, 'lng': lng,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"[ERROR] Weather: {e}")
        return {}

def fetch_regional_weather():
    """Fetch weather for key strategic locations"""
    locations = [
        {'name': 'Muscat', 'lat': 23.6, 'lng': 58.5},
        {'name': 'Strait of Hormuz', 'lat': 26.6, 'lng': 56.2},
        {'name': 'Salalah', 'lat': 17.0, 'lng': 54.1},
        {'name': 'Duqm', 'lat': 19.7, 'lng': 57.7},
        {'name': 'Sohar', 'lat': 24.3, 'lng': 56.7},
    ]
    results = []
    for loc in locations:
        weather = fetch_weather_openmeteo(loc['lat'], loc['lng'])
        weather['name'] = loc['name']
        results.append(weather)
    return results

def weather_to_czml(weather_data):
    """Convert weather data to CZML for CesiumJS overlay"""
    czml = [{"id": "document", "version": "1.0", "name": "MADA Weather Overlay"}]
    for w in weather_data:
        if w.get('lat') and w.get('lng'):
            czml.append({
                "id": f"weather-{w.get('name', 'unknown')}",
                "name": f"{w.get('name', '')} | {w.get('temperature', '?')}°C | Wind: {w.get('wind_speed', '?')}km/h",
                "position": {"cartographicDegrees": [w['lng'], w['lat'], 5000]},
                "label": {
                    "text": f"{w.get('name', '')}\n{w.get('temperature', '?')}°C",
                    "font": "13px IBM Plex Sans Arabic",
                    "fillColor": {"rgba": [201, 168, 76, 220]},
                    "showBackground": True,
                    "backgroundColor": {"rgba": [10, 14, 23, 200]},
                    "backgroundPadding": {"cartesian2": [8, 4]}
                }
            })
    return czml

if __name__ == "__main__":
    while True:
        weather = fetch_regional_weather()
        czml = weather_to_czml(weather)
        with open('/tmp/mada-weather-czml.json', 'w') as f:
            json.dump(czml, f, default=str)
        print(f"[{datetime.now()}] Weather overlay updated — {len(weather)} locations")
        time.sleep(600)  # Every 10 minutes

"""Routes API の step（道案内の区切り）ごとにカーブを計算し、交差点での曲がりを省いて採点を試すスクリプト"""

import os

import httpx
import polyline
from dotenv import load_dotenv

from app.services.scoring import curve_deg_per_km, route_length_km

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if API_KEY is None:
    raise RuntimeError("GOOGLE_MAPS_API_KEY が設定されていません。.env を確認してください")

URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

headers = {
    "Content-Tipe": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": (
        "routes.polyline.encodedPolyline,"
        "routes.legs.steps.polyline.encodedPolyline,"
        "routes.legs.steps.navigationInstruction.maneuver"
    ),
}

body = {
    "origin": {"location": {"latLng": {"latitude": 34.6946, "longitude": 135.1955}}},
    "destination": {"location": {"latLng": {"latitude": 34.7777, "longitude": 135.2636}}},
    "travelMode": "DRIVE",
    "languageCode": "ja"
}

response = httpx.post(URL, headers=headers, json=body)
print(response.status_code)

data = response.json()
route = data["routes"][0]
steps = route["legs"][0]["steps"]
print(f"step の数：{len(steps)}")

all_points = polyline.decode(route["polyline"]["encodedPolyline"])
print(f"区切りも含めたカーブ：{curve_deg_per_km(all_points):.1f} 度/km")

total_turn = 0.0
total_length = 0.0
for step in steps:
    points = polyline.decode(step["polyline"]["encodedPolyline"])
    length = route_length_km(points)
    if length == 0:
        continue
    turn = curve_deg_per_km(points) * length
    maneuver = step.get("navigationInstruction", {}).get("maneuver")
    print(f"{maneuver}：{length:.2f} km, 曲がった量{turn:.0f} 度")
    total_turn += turn
    total_length += length

print(f"区切りを省いたカーブ：{total_turn / total_length:.1f} 度/km")

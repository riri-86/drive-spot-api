"""Routes API からルートの点を取り、採点の関数を実データで試すためのスクリプト"""

import os

import httpx
import polyline
from dotenv import load_dotenv

from app.services.scoring import route_length_km
from app.services.scoring import (
    bearing_deg,
    curve_deg_per_km,
    detour_ratio,
    distance_km,
    route_length_km,
    turn_angle_deg,
)

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if API_KEY is None:
    raise RuntimeError("GOOGLR_MAPS_API_KEY が設定されていません。.env を確認してください")

URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

headers = {
    "Content-Tipe": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "routes.distanceMeters,routes.polyline.encodedPolyline",
}

body = {
    # 六甲山: origin (34.6946, 135.1955) → destination (34.7777, 135.2636)
    # 大阪市内: origin (34.6923, 135.5017) → destination (34.6665, 135.5011)
    "origin": {"location": {"latLng": {"latitude": 34.6946, "longitude": 135.1955}}},
    "destination": {"location": {"latLng": {"latitude": 34.7777, "longitude": 135.2636}}},
    "travelMode": "DRIVE",
}

response = httpx.post(URL, headers=headers, json=body)
print(response.status_code)

data = response.json()
encoded = data["routes"][0]["polyline"]["encodedPolyline"]

points = polyline.decode(encoded)
print(f"点の数：{len(points)}")
print(f"出発地：{points[0]}")
print(f"目的地：{points[-1]}")

print(f"自分で計算した道のり：{route_length_km(points):.2f} km")
print(f"Google の道のり：{data["routes"][0]["distanceMeters"] / 1000:.2f} km")
print(f"迂回率：{detour_ratio(points):.2f}")
print(f"カーブ：{curve_deg_per_km(points):.1f} 度/km")

bearings = []
for i in range(len(points) - 1):
    if distance_km(*points[i], *points[i + 1]) == 0:
        continue
    bearings.append(bearing_deg(*points[i], *points[i + 1]))

big = 0.0
small = 0.0
for i in range(len(bearings) - 1):
    angle = turn_angle_deg(bearings[i], bearings[i + 1])
    if angle >= 30:
        big += angle
        print(f"大きな曲り：{angle:.0f} 度")
    else:
        small += angle

print(f"30度以上の合計：{big:.0f} 度")
print(f"30度未満の合計：{small:.0f} 度")
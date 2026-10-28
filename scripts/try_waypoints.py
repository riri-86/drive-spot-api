import os

import httpx
import polyline
from dotenv import load_dotenv

from app.services.scoring import curve_deg_per_km_by_steps, route_length_km

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if API_KEY is None:
    raise RuntimeError("GOOGLE_MAPS_API_KEY が設定されていません。.env を確認してください")

URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "routes.distanceMeters,routes.legs.steps.polyline.encodedPolyline",
}


def compute_route(intermediates):
    body = {
        "origin": {"location": {"latLng": {"latitude": 34.6946, "longitude": 135.1955}}},
        "destination": {"location": {"latLng": {"latitude": 34.7777, "longitude": 135.2636}}},
        "travelMode": "DRIVE",
    }
    if intermediates:
        body["intermediates"] = intermediates

    response = httpx.post(URL, headers=headers, json=body)
    if response.status_code != 200:
        raise RuntimeError(f"Routes API がエラーを返しました: {response.status_code} {response.text}")
    return response.json()["routes"][0]


def steps_points_of(route):
    steps_points = []
    for leg in route["legs"]:
        for step in leg["steps"]:
            steps_points.append(polyline.decode(step["polyline"]["encodedPolyline"]))
    return steps_points


def show(label, route):
    steps_points = steps_points_of(route)
    print(label)
    print(f"  道のり: {route['distanceMeters']} m")
    print(f"  leg の数: {len(route['legs'])}, step の数: {len(steps_points)}")
    print(f"  区切りを省いたカーブ: {curve_deg_per_km_by_steps(steps_points):.1f} 度/km")


# 1. 経由地点なしで呼び、一番長い step の真ん中の点を経由地点にする
route = compute_route(None)
show("経由地点なし", route)

longest = []
for points in steps_points_of(route):
    if route_length_km(points) > route_length_km(longest):
        longest = points
waypoint = longest[len(longest) // 2]
print(f"経由地点: {waypoint}")

location = {"latLng": {"latitude": waypoint[0], "longitude": waypoint[1]}}

# 2. 同じ点を、普通の経由地点と via(通過するだけ)でおいて比べる
show("経由地点あり(普通)", compute_route([{"location": location}]))
show("経由地点あり(via)", compute_route([{"location": location, "via": True}]))

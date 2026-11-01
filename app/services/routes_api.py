"""GooGle Routes API を呼んで、ルートの点を受け取る"""

import os

import httpx
import polyline
from dotenv import load_dotenv

load_dotenv()

URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
FIELD_MASK = "routes.legs.steps.polyline.encodedPolyline"


class RoutesApiError(Exception):
    """Routes API からルートを受け取れなかった時のエラー"""


def to_location(point: tuple[float,float]) -> dict:
    """(緯度,経度) を、Routes API が読める形の辞書にする"""
    return {"location": {"latLng": {"latitude": point[0], "longitude": point[1]}}}


def fetch_route_steps(
        origin: tuple[float, float],
        destination: tuple[float, float],
        vias: list[tuple[float, float]] | None = None,
) -> list[list[tuple[float, float]]]:
    """出発地・目的地・経由地点(via)からルートを取得し、step ごとの点のリストを返す"""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if api_key is None:
        raise RoutesApiError("GOOGLE_MAPS_API_KEY が設定されていません。.env を確認してください")

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    }
    body = {
        "origin": to_location(origin),
        "destination": to_location(destination),
        "travelMode": "DRIVE",
    }
    if vias:
        intermediates = []
        for point in vias:
            intermediate = to_location(point)
            intermediate["via"] = True
            intermediates.append(intermediate)
        body["intermediates"] = intermediates

    response = httpx.post(URL, headers=headers, json=body)
    if response.status_code != 200:
        raise RoutesApiError(f"Routes API がエラーを返しました: {response.status_code} {response.text}")

    routes = response.json().get("routes")
    if not routes:
        raise RoutesApiError("ルートが見つかりませんでした。出発地・目的地・経由地点を確認してください")

    steps_points = []
    for leg in routes[0]["legs"]:
        for step in leg["steps"]:
            steps_points.append(polyline.decode(step["polyline"]["encodedPolyline"]))
    return steps_points

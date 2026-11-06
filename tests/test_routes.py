"""POST /routes のテスト(Google は呼ばず、fetch_route_steps を作り物に入れ替える)"""

from app.routers import routes as routes_router
from app.services.routes_api import RoutesApiError

STEP_NORTH = [(34.0, 135.0), (34.01, 135.0)]
STEP_EAST = [(34.01, 135.0), (34.01, 135.01)]

ROUTE_DATA = {
    "name": "テスト用ルート",
    "origin_lat": 34.0,
    "origin_lng": 135.0,
    "destination_lat": 34.01,
    "destination_lng": 135.01,
    "vias": [{"lat": 34.01, "lng": 135.0}],
}


def test_create_route(client, monkeypatch):
    def fake_fetch_route_steps(origin, destination, vias):
        return [STEP_NORTH, STEP_EAST]

    monkeypatch.setattr(routes_router, "fetch_route_steps", fake_fetch_route_steps)

    response = client.post("/routes", json=ROUTE_DATA)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "テスト用ルート"
    assert body["vias"] == [{"position": 1, "lat": 34.01, "lng": 135.0}]
    assert body["curve_deg_per_km"] == 0


def test_create_route_returns_502_when_google_fails(client, monkeypatch):
    def fake_fetch_route_steps(origin, destination, vias):
        raise RoutesApiError("ルートが見つかりませんでした")

    monkeypatch.setattr(routes_router, "fetch_route_steps", fake_fetch_route_steps)

    response = client.post("/routes", json=ROUTE_DATA)

    assert response.status_code == 502
    assert response.json()["detail"] == "ルートが見つかりませんでした"


def test_create_route_returns_422_when_start_equals_end(client,monkeypatch):
    def fake_fetch_route_steps(origin, destination, vias):
        return [[(34.0, 135.0), (34.01, 135.0), (34.0, 135.0)]]

    monkeypatch.setattr(routes_router, "fetch_route_steps", fake_fetch_route_steps)

    response = client.post("/routes", json=ROUTE_DATA)

    assert response.status_code == 422
    assert "迂回率" in response.json()["detail"]


def test_create_route_pass_vias_in_order(client, monkeypatch):
    sent = {}

    def fake_fetch_route_steps(origin, destination, vias):
        sent["vias"] = vias
        return [STEP_NORTH, STEP_EAST]

    monkeypatch.setattr(routes_router, "fetch_route_steps", fake_fetch_route_steps)

    data = {**ROUTE_DATA, "vias": [{"lat": 34.01, "lng": 135.0}, {"lat": 34.02, "lng": 135.0}]}
    response = client.post("/routes", json=data)

    assert sent["vias"] == [(34.01, 135.0), (34.02, 135.0)]
    assert [via["position"] for via in response.json()["vias"]] == [1, 2]

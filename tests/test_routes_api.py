"""routes_api のテスト(本物の Google は呼ばず、作り物の返事を使う)"""

import httpx
import polyline
import pytest

from app.services.routes_api import RoutesApiError, fetch_route_steps

OSAKA = (34.6937, 135.5023)
KOBE = (34.6901, 135.1955)


class FakeResponse:
    """httpx の返事のふりをする"""

    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data
        self.text = str(data)

    def json(self):
        return self.data


def test_fetch_route_steps_returns_points_of_each_step(monkeypatch):
    step1 = [(34.0, 135.0), (34.01, 135.0)]
    step2 = [(34.01, 135.0), (34.01, 135.01)]
    data = {
        "routes":[
            {
                "legs": [
                    {
                        "steps": [
                            {"polyline": {"encodedPolyline": polyline.encode(step1)}},
                            {"polyline": {"encodedPolyline": polyline.encode(step2)}},
                        ]
                    }
                ]
            }
        ]
    }

    def fake_post(url, headers, json):
        return FakeResponse(200, data)

    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "test-key")
    monkeypatch.setattr(httpx, "post", fake_post)

    assert fetch_route_steps(OSAKA,KOBE) == [step1, step2]


def test_fetch_route_steps_raises_error_when_not_200(monkeypatch):
    def fake_post(url, headers, json):
        return FakeResponse(400, {"error": {"message": "Unknown name"}})

    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "test-key")
    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(RoutesApiError):
        fetch_route_steps(OSAKA, KOBE)


def test_fetch_route_steps_raises_error_when_no_routes(monkeypatch):
    def fake_post(url, headers, json):
        return FakeResponse(200, {})

    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "test-key")
    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(RoutesApiError, match="ルートが見つかりませんでした"):
        fetch_route_steps(OSAKA, KOBE)


def test_fetch_route_steps_raises_error_when_no_api_key(monkeypatch):
    def fake_post(url, headers, json):
        raise AssertionError("APIキーがないのに Google を呼ぼうとした")

    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(RoutesApiError, match="GOOGLE_MAPS_API_KEY"):
        fetch_route_steps(OSAKA, KOBE)


def test_fetch_route_steps_sends_vias_as_via(monkeypatch):
    sent = {}
    points = [(34.0, 135.0), (34.01, 135.0)]
    data = {"routes": [{"legs": [{"steps": [{"polyline": {"encodedPolyline": polyline.encode(points)}}]}]}]}

    def fake_post(url, headers, json):
        sent["body"] = json
        return FakeResponse(200, data)

    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "test-key")
    monkeypatch.setattr(httpx, "post", fake_post)

    fetch_route_steps(OSAKA, KOBE, [(34.75, 135.25)])

    assert sent["body"]["intermediates"] == [
        {"location": {"latLng": {"latitude": 34.75, "longitude": 135.25}}, "via": True}
    ]
    
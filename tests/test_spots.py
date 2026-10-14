from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_spot_rating_too_high():
    data = {
        "name":"六甲山",
        "address": "兵庫県神戸市灘区",
        "category": "山道",
        "memo": "テスト用",
        "visited": False,
        "rating": 6,
    }
    response = client.post("/spots", json=data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "rating"]

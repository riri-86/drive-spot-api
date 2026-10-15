def test_create_spot_rating_too_high(client):
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


def test_create_spot(client):
    data = {
        "name": "六甲山",
        "address": "兵庫県神戸市灘区",
        "category": "山道",
        "memo": "テスト用",
        "visited": False,
        "rating": 4,
    }
    response = client.post("/spots", json=data)
    assert response.status_code == 201

    body = response.json()
    assert body["name"] == "六甲山"
    assert body["rating"] == 4
    assert "id" in body

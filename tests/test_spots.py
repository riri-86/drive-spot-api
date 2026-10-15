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


def test_get_spot_not_found(client):
    response = client.get("/spots/9999")
    assert response.status_code == 404


def test_get_spot(client):
    data = {
        "name": "六甲山",
        "address": "兵庫県神戸市灘区",
        "category": "山道",
        "memo": "テスト用",
        "visited": False,
        "rating": 4,
    }
    created = client.post("/spots", json=data).json()
    spot_id = created["id"]

    response = client.get(f"/spots/{spot_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "六甲山"


def test_update_spot(client):
    data = {
        "name": "六甲山",
        "address": "兵庫県神戸市灘区",
        "category": "山道",
        "memo": "テスト用",
        "visited": False,
        "rating": 4,
    }
    created = client.post("/spots", json=data).json()
    spot_id = created["id"]

    new_data = {**data, "visited": True, "rating": 5}
    response = client.put(f"/spots/{spot_id}", json=new_data)
    assert response.status_code == 200
    assert response.json()["visited"] is True
    assert response.json()["rating"] == 5

    response = client.get(f"/spots/{spot_id}")
    assert response.json()["rating"] == 5


def test_delete_spot(client):
    data = {
        "name": "六甲山",
        "address": "兵庫県神戸市灘区",
        "category": "山道",
        "memo": "テスト用",
        "visited": False,
        "rating": 4,
    }
    created = client.post("/spots", json=data).json()
    spot_id = created["id"]

    response = client.delete(f"/spots/{spot_id}")
    assert response.status_code == 204

    response = client.get(f"/spots/{spot_id}")
    assert response.status_code == 404
    
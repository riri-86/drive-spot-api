SPOT_DATA = {
    "name": "六甲山",
    "address": "兵庫県神戸市",
    "category": "山道",
    "memo": "テスト用",
    "visited": False,
    "rating": 4,
}


def create_spot(client):
    return client.post("/spots", json=SPOT_DATA).json()


def test_create_spot_rating_too_high(client):
    data = {**SPOT_DATA, "rating": 6}
    response = client.post("/spots", json=data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "rating"]
 

def test_create_spot(client):
    response = client.post("/spots", json=SPOT_DATA)
    assert response.status_code == 201

    body = response.json()
    assert body["name"] == "六甲山"
    assert body["rating"] == 4
    assert "id" in body


def test_get_spot_not_found(client):
    response = client.get("/spots/9999")
    assert response.status_code == 404


def test_get_spot(client):
    spot_id = create_spot(client)["id"]

    response = client.get(f"/spots/{spot_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "六甲山"


def test_update_spot(client):
    spot_id = create_spot(client)["id"]

    new_data = {**SPOT_DATA, "visited": True, "rating": 5}
    response = client.put(f"/spots/{spot_id}", json=new_data)
    assert response.status_code == 200
    assert response.json()["visited"] is True
    assert response.json()["rating"] == 5

    response = client.get(f"/spots/{spot_id}")
    assert response.json()["rating"] == 5


def test_delete_spot(client):
    spot_id = create_spot(client)["id"]

    response = client.delete(f"/spots/{spot_id}")
    assert response.status_code == 204

    response = client.get(f"/spots/{spot_id}")
    assert response.status_code == 404



def test_create_spot_without_api_key_returns_401(client):
    del client.headers["X-API-Key"]

    response = client.post("/spots", json=SPOT_DATA)

    assert response.status_code == 401
    assert client.get("/spots").json() == []


def test_create_spot_with_wrong_api_key_returns_401(client):
    response = client.post("/spots", json=SPOT_DATA, headers={"X-API-Key": "wrong-key"})

    assert response.status_code == 401


def test_create_spot_returns_500_when_admin_api_key_not_set(client, monkeypatch):
    monkeypatch.delenv("ADMIN_API_KEY")

    response = client.post("/spots", json=SPOT_DATA)

    assert response.status_code == 500

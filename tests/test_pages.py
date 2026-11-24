def test_map_page_contains_maps_key(client, monkeypatch):
    monkeypatch.setenv("GOOGLE_MAPS_JS_API_KEY", "test-maps-key")

    response = client.get("/map")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "key=test-maps-key" in response.text

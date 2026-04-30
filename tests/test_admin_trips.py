from fastapi.testclient import TestClient

TRIP_1 = {"name": "Trip 1", "duration_days": 2}


def test_create_trip_success(client: TestClient, admin_headers: dict[str:str]):
    response = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["name"] == "Trip 1"
    assert data["slug"] == "trip-1"
    assert data["description"] is None
    assert data["duration_days"] == 2
    assert data["is_active"] is False
    assert "created_at" in data
    assert "updated_at" in data


def test_create_trip_exists(client: TestClient, admin_headers: dict[str, str]):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    assert trip.status_code == 201

    response = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    assert response.status_code == 409

    error = response.json()["error"]
    assert error["code"] == "TRIP_ALREADY_EXISTS"
    assert error["message"] == "Trip slug already exists"

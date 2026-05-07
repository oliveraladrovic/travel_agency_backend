from fastapi.testclient import TestClient

TRIP_1 = {"name": "Trip 1", "duration_days": 2}
TRIP_2 = {"name": "Trip 2", "duration_days": 3}


def test_create_trip_success(client: TestClient, admin_headers: dict[str, str]):
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


def test_list_trips_admin_success(client: TestClient, admin_headers: dict[str, str]):
    client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    client.post("/admin/trips/", headers=admin_headers, json=TRIP_2)

    response = client.get("/admin/trips/", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_trip_admin_success(client: TestClient, admin_headers: dict[str, str]):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip.json()["id"]

    response = client.get(f"/admin/trips/{trip_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["id"] == trip_id
    assert response.json()["name"] == TRIP_1["name"]


def test_get_trip_admin_404(client: TestClient, admin_headers: dict[str, str]):
    client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)

    response = client.get("/admin/trips/999", headers=admin_headers)
    assert response.status_code == 404

    error = response.json()["error"]
    assert error["code"] == "TRIP_NOT_FOUND"
    assert error["message"] == "Trip not found"


def test_delete_trip_hard(client: TestClient, admin_headers: dict[str, str]):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    assert trip.status_code == 201

    trip_id = trip.json()["id"]
    delete = client.delete(f"/admin/trips/{trip_id}", headers=admin_headers)
    assert delete.status_code == 204

    response = client.get(f"/admin/trips/{trip_id}", headers=admin_headers)
    assert response.status_code == 404

from fastapi.testclient import TestClient
from datetime import date, timedelta

TRIP_1 = {"name": "Trip 1", "duration_days": 2}
TRIP_2 = {"name": "Trip 2", "duration_days": 3}
START_DATE = date.today() + timedelta(days=1)
PAST_DATE = date.today() - timedelta(days=1)
DEP_DATA_1 = {
    "start_date": START_DATE.isoformat(),
    "capacity": 45,
    "price_per_seat": 59.99,
}
DEP_DATA_2 = {
    "start_date": START_DATE.isoformat(),
    "capacity": 60,
    "price_per_seat": 79.99,
}


def test_create_departure_success(client: TestClient, admin_headers: dict[str, str]):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    assert trip.status_code == 201

    trip_id = trip.json()["id"]
    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    response = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["trip_id"] == departure_data["trip_id"]
    assert date.fromisoformat(data["start_date"]) == START_DATE
    assert data["capacity"] == departure_data["capacity"]
    assert float(data["price_per_seat"]) == departure_data["price_per_seat"]
    assert data["is_active"] is False
    assert "created_at" in data
    assert "updated_at" in data


def test_create_departure_past(client: TestClient, admin_headers: dict[str, str]):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    assert trip.status_code == 201

    trip_id = trip.json()["id"]
    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    departure_data["start_date"] = PAST_DATE.isoformat()
    response = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    assert response.status_code == 400

    error = response.json()["error"]
    assert error["code"] == "INVALID_DEPARTURE_DATE"
    assert error["message"] == "Departure date must be in future"


def test_list_departures_admin_success(
    client: TestClient, admin_headers: dict[str, str]
):
    trip1 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip2 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_2)
    departure_data1 = DEP_DATA_1.copy()
    departure_data2 = DEP_DATA_2.copy()
    departure_data1["trip_id"] = trip1.json()["id"]
    departure_data2["trip_id"] = trip2.json()["id"]
    client.post("/admin/departures/", headers=admin_headers, json=departure_data1)
    client.post("/admin/departures/", headers=admin_headers, json=departure_data2)

    response = client.get("/admin/departures/", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_departure_admin_success(client: TestClient, admin_headers: dict[str, str]):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    assert departure.status_code == 201

    departure_id = departure.json()["id"]
    response = client.get(f"/admin/departures/{departure_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["id"] == departure_id
    assert response.json()["capacity"] == departure_data["capacity"]


def test_get_departure_admin_404(client: TestClient, admin_headers: dict[str, str]):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip.json()["id"]
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    assert departure.status_code == 201

    response = client.get("/admin/departures/999", headers=admin_headers)
    assert response.status_code == 404

    error = response.json()["error"]
    assert error["code"] == "DEPARTURE_NOT_FOUND"
    assert error["message"] == "Departure not found"


def test_update_departure_success(client: TestClient, admin_headers: dict[str, str]):
    trip1 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip1_id = trip1.json()["id"]
    trip2 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_2)
    trip2_id = trip2.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip1_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    departure_id = departure.json()["id"]

    response = client.patch(
        f"/admin/departures/{departure_id}",
        headers=admin_headers,
        json={"trip_id": trip2_id, "is_active": True},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == departure_id
    assert data["trip_id"] == trip2_id
    assert data["is_active"] is True


def test_update_departure_empty(client: TestClient, admin_headers: dict[str, str]):
    trip1 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip1_id = trip1.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip1_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    departure_id = departure.json()["id"]

    response = client.patch(
        f"/admin/departures/{departure_id}",
        headers=admin_headers,
        json={},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == departure_id
    assert data["trip_id"] == trip1_id
    assert data["is_active"] is False


def test_update_departure_no_trip(client: TestClient, admin_headers: dict[str, str]):
    trip1 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip1_id = trip1.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip1_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    departure_id = departure.json()["id"]

    response = client.patch(
        f"/admin/departures/{departure_id}",
        headers=admin_headers,
        json={"trip_id": 999, "is_active": True},
    )
    assert response.status_code == 404

    error = response.json()["error"]
    assert error["code"] == "TRIP_NOT_FOUND"
    assert error["message"] == "Trip not found"


def test_update_departure_past_date(client: TestClient, admin_headers: dict[str, str]):
    trip1 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip1_id = trip1.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip1_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    departure_id = departure.json()["id"]

    response = client.patch(
        f"/admin/departures/{departure_id}",
        headers=admin_headers,
        json={"start_date": PAST_DATE.isoformat()},
    )
    assert response.status_code == 400

    error = response.json()["error"]
    assert error["code"] == "INVALID_DEPARTURE_DATE"
    assert error["message"] == "Departure date must be in future"


def test_delete_departure_hard(client: TestClient, admin_headers: dict[str, str]):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    assert departure.status_code == 201

    departure_id = departure.json()["id"]
    delete = client.delete(f"/admin/departures/{departure_id}", headers=admin_headers)
    assert delete.status_code == 204

    response = client.get(f"/admin/departures/{departure_id}", headers=admin_headers)
    assert response.status_code == 404

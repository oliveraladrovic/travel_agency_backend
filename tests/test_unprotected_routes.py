from fastapi.testclient import TestClient
from datetime import date, timedelta

TRIP_1 = {"name": "Trip 1", "duration_days": 2, "is_active": True}
TRIP_2 = {"name": "Trip 2", "duration_days": 3}
START_DATE = date.today() + timedelta(days=1)
DEP_DATA_1 = {
    "start_date": START_DATE.isoformat(),
    "capacity": 45,
    "price_per_seat": 59.99,
}
DEP_DATA_2 = {
    "start_date": START_DATE.isoformat(),
    "capacity": 60,
    "price_per_seat": 79.99,
    "is_active": True,
}


def test_list_unprotected_trips_success(
    client: TestClient, admin_headers: dict[str, str]
):
    trip1 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    assert trip1.status_code == 201
    trip2 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_2)
    assert trip2.status_code == 201

    response = client.get("/trips/")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_unprotected_trip_success(
    client: TestClient, admin_headers: dict[str, str]
):
    trip1 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    assert trip1.status_code == 201

    response = client.get(f"/trips/{trip1.json()['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == TRIP_1["name"]


def test_get_unprotected_trip_inactive(
    client: TestClient, admin_headers: dict[str, str]
):
    trip2 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_2)
    assert trip2.status_code == 201

    response = client.get(f"/trips/{trip2.json()['id']}")
    assert response.status_code == 404

    error = response.json()["error"]
    assert error["code"] == "TRIP_NOT_FOUND"
    assert error["message"] == "Trip not found"


def test_get_unprotected_trip_404(client: TestClient, admin_headers: dict[str, str]):
    trip2 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_2)
    assert trip2.status_code == 201

    response = client.get("/trips/999")
    assert response.status_code == 404

    error = response.json()["error"]
    assert error["code"] == "TRIP_NOT_FOUND"
    assert error["message"] == "Trip not found"


def test_list_unprotected_departures_by_trip_success(
    client: TestClient, admin_headers: dict[str, str]
):
    trip1 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip1.json()["id"]

    departure_data1 = DEP_DATA_1.copy()
    departure_data1["trip_id"] = trip_id
    departure1 = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data1
    )
    assert departure1.status_code == 201

    departure_data2 = DEP_DATA_2.copy()
    departure_data2["trip_id"] = trip_id
    departure2 = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data2
    )
    assert departure2.status_code == 201

    response = client.get(f"/trips/{trip_id}/departures")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == departure2.json()["id"]


def test_list_unprotected_departures_by_trip_inactive(
    client: TestClient, admin_headers: dict[str, str]
):
    trip2 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_2)
    trip_id = trip2.json()["id"]

    departure_data1 = DEP_DATA_1.copy()
    departure_data1["trip_id"] = trip_id
    departure1 = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data1
    )
    assert departure1.status_code == 201

    departure_data2 = DEP_DATA_2.copy()
    departure_data2["trip_id"] = trip_id
    departure2 = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data2
    )
    assert departure2.status_code == 201

    response = client.get(f"/trips/{trip_id}/departures")
    assert response.status_code == 404

    error = response.json()["error"]
    assert error["code"] == "TRIP_NOT_FOUND"
    assert error["message"] == "Trip not found"


def test_list_unprotected_departures_by_trip_not_existing(
    client: TestClient, admin_headers: dict[str, str]
):
    trip2 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_2)
    trip_id = trip2.json()["id"]

    departure_data1 = DEP_DATA_1.copy()
    departure_data1["trip_id"] = trip_id
    departure1 = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data1
    )
    assert departure1.status_code == 201

    departure_data2 = DEP_DATA_2.copy()
    departure_data2["trip_id"] = trip_id
    departure2 = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data2
    )
    assert departure2.status_code == 201

    response = client.get("/trips/999/departures")
    assert response.status_code == 404

    error = response.json()["error"]
    assert error["code"] == "TRIP_NOT_FOUND"
    assert error["message"] == "Trip not found"


def test_get_unprotected_departure_success(
    client: TestClient, admin_headers: dict[str, str]
):
    trip1 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip1.json()["id"]

    departure_data = DEP_DATA_2.copy()
    departure_data["trip_id"] = trip_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    assert departure.status_code == 201

    departure_id = departure.json()["id"]
    response = client.get(f"/departures/{departure_id}")
    assert response.status_code == 200
    assert response.json()["capacity"] == departure_data["capacity"]


def test_get_unprotected_departure_inactive(
    client: TestClient, admin_headers: dict[str, str]
):
    trip1 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip1.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    assert departure.status_code == 201

    departure_id = departure.json()["id"]
    response = client.get(f"/departures/{departure_id}")
    assert response.status_code == 404

    error = response.json()["error"]
    assert error["code"] == "DEPARTURE_NOT_FOUND"
    assert error["message"] == "Departure not found"


def test_get_unprotected_departure_404(
    client: TestClient, admin_headers: dict[str, str]
):
    trip1 = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip1.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    assert departure.status_code == 201

    response = client.get("/departures/999")
    assert response.status_code == 404

    error = response.json()["error"]
    assert error["code"] == "DEPARTURE_NOT_FOUND"
    assert error["message"] == "Departure not found"

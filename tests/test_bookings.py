from fastapi.testclient import TestClient
from datetime import date, timedelta

from travel_agency_backend.utils.enums import BookingStatus

TRIP_1 = {"name": "Trip 1", "duration_days": 2, "is_active": True}
START_DATE = date.today() + timedelta(days=30)
DEP_DATA_1 = {
    "start_date": START_DATE.isoformat(),
    "capacity": 45,
    "price_per_seat": 59.99,
    "is_active": True,
}


def test_create_booking_success(
    client: TestClient, admin_headers: dict[str, str], user_headers: dict[str, str]
):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    departure_id = departure.json()["id"]

    booking_data = {"departure_id": departure_id, "seats_reserved": 2}
    response = client.post("/bookings/", headers=user_headers, json=booking_data)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["departure_id"] == departure_id
    assert data["seats_reserved"] == 2
    assert float(data["price_per_seat_snapshot"]) == 59.99
    assert float(data["total_price_snapshot"]) == 59.99 * 2
    assert data["status"] == BookingStatus.RESERVED
    assert "created_at" in data
    assert "updated_at" in data
    assert data["payment_deadline"] == (START_DATE - timedelta(days=15)).isoformat()


def test_create_booking_no_departure(
    client: TestClient, admin_headers: dict[str, str], user_headers: dict[str, str]
):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    client.post("/admin/departures/", headers=admin_headers, json=departure_data)

    booking_data = {"departure_id": 999, "seats_reserved": 2}
    response = client.post("/bookings/", headers=user_headers, json=booking_data)
    assert response.status_code == 400

    error = response.json()["error"]
    assert error["code"] == "DEPARTURE_NOT_AVAILABLE"
    assert error["message"] == "Departure not available"


def test_create_booking_departure_not_active(
    client: TestClient, admin_headers: dict[str, str], user_headers: dict[str, str]
):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    departure_data["is_active"] = False
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    departure_id = departure.json()["id"]

    booking_data = {"departure_id": departure_id, "seats_reserved": 2}
    response = client.post("/bookings/", headers=user_headers, json=booking_data)
    assert response.status_code == 400

    error = response.json()["error"]
    assert error["code"] == "DEPARTURE_NOT_AVAILABLE"
    assert error["message"] == "Departure not available"


def test_create_booking_trip_not_active(
    client: TestClient, admin_headers: dict[str, str], user_headers: dict[str, str]
):
    trip_data = TRIP_1.copy()
    trip_data["is_active"] = False
    trip = client.post("/admin/trips/", headers=admin_headers, json=trip_data)
    trip_id = trip.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    departure_id = departure.json()["id"]

    booking_data = {"departure_id": departure_id, "seats_reserved": 2}
    response = client.post("/bookings/", headers=user_headers, json=booking_data)
    assert response.status_code == 400

    error = response.json()["error"]
    assert error["code"] == "DEPARTURE_NOT_AVAILABLE"
    assert error["message"] == "Departure not available"


def test_create_booking_exceeds_user_limit(
    client: TestClient, admin_headers: dict[str, str], user_headers: dict[str, str]
):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    departure_id = departure.json()["id"]

    booking_data1 = {"departure_id": departure_id, "seats_reserved": 6}
    booking1 = client.post("/bookings/", headers=user_headers, json=booking_data1)
    assert booking1.status_code == 201

    booking_data2 = {"departure_id": departure_id, "seats_reserved": 6}
    response = client.post("/bookings/", headers=user_headers, json=booking_data2)
    assert response.status_code == 409

    error = response.json()["error"]
    assert error["code"] == "UNAVAILABLE_CAPACITY"
    assert error["message"] == "Unavailable capacity"


def test_create_booking_exceeds_capacity(
    client: TestClient, admin_headers: dict[str, str], user_headers: dict[str, str]
):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    departure_data["capacity"] = 8
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    departure_id = departure.json()["id"]

    booking_data1 = {"departure_id": departure_id, "seats_reserved": 6}
    booking1 = client.post("/bookings/", headers=user_headers, json=booking_data1)
    assert booking1.status_code == 201

    booking_data2 = {"departure_id": departure_id, "seats_reserved": 3}
    response = client.post("/bookings/", headers=user_headers, json=booking_data2)
    assert response.status_code == 409

    error = response.json()["error"]
    assert error["code"] == "UNAVAILABLE_CAPACITY"
    assert error["message"] == "Unavailable capacity"


def test_list_bookings_success(
    client: TestClient, admin_headers: dict[str, str], user_headers: dict[str, str]
):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    departure_id = departure.json()["id"]

    booking_data1 = {"departure_id": departure_id, "seats_reserved": 2}
    booking_data2 = {"departure_id": departure_id, "seats_reserved": 3}
    client.post("/bookings/", headers=user_headers, json=booking_data1)
    client.post("/bookings/", headers=user_headers, json=booking_data2)

    response = client.get("/bookings/me", headers=user_headers)
    assert response.status_code == 200


def test_list_summary_success(
    client: TestClient, admin_headers: dict[str, str], user_headers: dict[str, str]
):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    departure_id = departure.json()["id"]

    booking_data1 = {"departure_id": departure_id, "seats_reserved": 2}
    booking_data2 = {"departure_id": departure_id, "seats_reserved": 3}
    client.post("/bookings/", headers=user_headers, json=booking_data1)
    client.post("/bookings/", headers=user_headers, json=booking_data2)

    response = client.get("/bookings/me/summary", headers=user_headers)
    assert response.status_code == 200

    data = response.json()
    assert data[0]["total_seats"] == 5
    assert len(data[0]["bookings"]) == 2


def test_get_booking_success(
    client: TestClient, admin_headers: dict[str, str], user_headers: dict[str, str]
):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    departure_id = departure.json()["id"]

    booking_data = {"departure_id": departure_id, "seats_reserved": 2}
    booking = client.post("/bookings/", headers=user_headers, json=booking_data)
    booking_id = booking.json()["id"]

    response = client.get(f"/bookings/{booking_id}", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["id"] == booking_id


def test_get_booking_not_existing(
    client: TestClient, admin_headers: dict[str, str], user_headers: dict[str, str]
):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    departure_id = departure.json()["id"]

    booking_data = {"departure_id": departure_id, "seats_reserved": 2}
    client.post("/bookings/", headers=user_headers, json=booking_data)

    response = client.get("/bookings/999", headers=user_headers)
    assert response.status_code == 404

    error = response.json()["error"]
    assert error["code"] == "BOOKING_NOT_FOUND"
    assert error["message"] == "Booking not found"


def test_get_booking_other_user(
    client: TestClient,
    admin_headers: dict[str, str],
    user_headers: dict[str, str],
    user_headers2: dict[str, str],
):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    departure_id = departure.json()["id"]

    booking_data = {"departure_id": departure_id, "seats_reserved": 2}
    client.post("/bookings/", headers=user_headers, json=booking_data)

    booking_data2 = {"departure_id": departure_id, "seats_reserved": 3}
    user2_booking = client.post("/bookings/", headers=user_headers2, json=booking_data2)
    user2_booking_id = user2_booking.json()["id"]

    response = client.get(f"/bookings/{user2_booking_id}", headers=user_headers)
    assert response.status_code == 404

    error = response.json()["error"]
    assert error["code"] == "BOOKING_NOT_FOUND"
    assert error["message"] == "Booking not found"

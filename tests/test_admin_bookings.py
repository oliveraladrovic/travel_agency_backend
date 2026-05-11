from fastapi.testclient import TestClient
from datetime import date, timedelta

TRIP_1 = {"name": "Trip 1", "duration_days": 2, "is_active": True}
START_DATE = date.today() + timedelta(days=30)
DEP_DATA_1 = {
    "start_date": START_DATE.isoformat(),
    "capacity": 45,
    "price_per_seat": 59.99,
    "is_active": True,
}


def test_list_bookings_admin(
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
    client.post("/bookings/", headers=user_headers2, json=booking_data2)

    response = client.get("/admin/bookings/", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_bookings_admin_unauthorized(
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
    client.post("/bookings/", headers=user_headers2, json=booking_data2)

    response = client.get("/admin/bookings/")
    assert response.status_code == 401


def test_get_booking_admin_success(
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

    response = client.get(f"/admin/bookings/{booking_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["id"] == booking_id


def test_get_booking_admin_forbidden(
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

    response = client.get(f"/admin/bookings/{booking_id}", headers=user_headers)
    assert response.status_code == 403


def test_get_booking_admin_404(
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

    response = client.get("/admin/bookings/999", headers=admin_headers)
    assert response.status_code == 404

    error = response.json()["error"]
    assert error["code"] == "BOOKING_NOT_FOUND"
    assert error["message"] == "Booking not found"

from fastapi.testclient import TestClient
from datetime import date, timedelta

from travel_agency_backend.utils.enums import UserRole
from travel_agency_backend.utils.enums import BookingStatus

FIRST_USER = {"email": "first.user@example.com", "password": "first_user"}
TRIP_1 = {"name": "Trip 1", "duration_days": 2, "is_active": True}
START_DATE = date.today() + timedelta(days=30)
DEP_DATA_1 = {
    "start_date": START_DATE.isoformat(),
    "capacity": 45,
    "price_per_seat": 59.99,
    "is_active": True,
}


def test_update_user_role_success(client: TestClient, admin_headers: dict[str, str]):
    user = client.post(
        "/auth/register",
        json=FIRST_USER,
    )
    user_id = user.json()["id"]

    response = client.post(
        f"/admin/users/{user_id}/role",
        headers=admin_headers,
        json={"role": UserRole.ADMIN},
    )
    assert response.status_code == 200
    assert response.json()["role"] == UserRole.ADMIN.value


def test_update_user_role_unauthorized(
    client: TestClient, admin_headers: dict[str, str]
):
    user = client.post(
        "/auth/register",
        json=FIRST_USER,
    )
    user_id = user.json()["id"]

    response = client.post(
        f"/admin/users/{user_id}/role",
        json={"role": UserRole.ADMIN},
    )
    assert response.status_code == 401


def test_update_user_status_success(client: TestClient, admin_headers: dict[str, str]):
    user = client.post(
        "/auth/register",
        json=FIRST_USER,
    )
    user_id = user.json()["id"]

    response = client.post(
        f"/admin/users/{user_id}/status",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_update_user_status_active_booking(
    client: TestClient, admin_headers: dict[str, str]
):
    trip = client.post("/admin/trips/", headers=admin_headers, json=TRIP_1)
    trip_id = trip.json()["id"]

    departure_data = DEP_DATA_1.copy()
    departure_data["trip_id"] = trip_id
    departure = client.post(
        "/admin/departures/", headers=admin_headers, json=departure_data
    )
    departure_id = departure.json()["id"]

    register = client.post(
        "/auth/register",
        json=FIRST_USER,
    )
    assert register.status_code == 201

    login = client.post(
        "/auth/login",
        data={"username": FIRST_USER["email"], "password": FIRST_USER["password"]},
    )
    assert login.status_code == 200

    token = login.json()["access_token"]
    booking_data = {"departure_id": departure_id, "seats_reserved": 2}
    booking = client.post(
        "/bookings/", headers={"Authorization": f"Bearer {token}"}, json=booking_data
    )
    assert booking.status_code == 201
    assert booking.json()["status"] == BookingStatus.RESERVED.value

    user_id = register.json()["id"]
    response = client.post(
        f"/admin/users/{user_id}/status",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert response.status_code == 409

    error = response.json()["error"]
    assert error["code"] == "USER_HAS_ACTIVE_BOOKINGS"
    assert error["message"] == "User has active bookings"

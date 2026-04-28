from fastapi.testclient import TestClient

FIRST_USER = {"email": "first.user@example.com", "password": "first_user"}
SAME_EMAIL_USER = {"email": "first.user@example.com", "password": "same_email_user"}


def test_register_user_success(client: TestClient):
    response = client.post(
        "/auth/register",
        json=FIRST_USER,
    )
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["email"] == FIRST_USER["email"]
    assert data["is_active"] is True


def test_register_user_email_exists(client: TestClient):
    user1 = client.post(
        "/auth/register",
        json=FIRST_USER,
    )
    assert user1.status_code == 201

    user2 = client.post(
        "/auth/register",
        json=SAME_EMAIL_USER,
    )
    assert user2.status_code == 409

    error = user2.json()["error"]
    assert error["code"] == "EMAIL_ALREADY_EXISTS"
    assert error["message"] == "Email already exists"

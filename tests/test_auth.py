from fastapi.testclient import TestClient

FIRST_USER = {"email": "first.user@example.com", "password": "first_user"}
SAME_EMAIL_USER = {"email": "first.user@example.com", "password": "same_email_user"}
SECOND_USER = {"email": "second.user@example.com", "password": "second_user"}


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


def test_login_user_success(client: TestClient):
    register = client.post(
        "/auth/register",
        json=FIRST_USER,
    )
    assert register.status_code == 201

    response = client.post(
        "/auth/login",
        data={"username": FIRST_USER["email"], "password": FIRST_USER["password"]},
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


def test_login_user_invalid_password(client: TestClient):
    register = client.post(
        "/auth/register",
        json=FIRST_USER,
    )
    assert register.status_code == 201

    response = client.post(
        "/auth/login",
        data={
            "username": SAME_EMAIL_USER["email"],
            "password": SAME_EMAIL_USER["password"],
        },
    )
    assert response.status_code == 401

    error = response.json()["error"]
    assert error["code"] == "INVALID_CREDENTIALS"
    assert error["message"] == "Invalid email or password"


def test_login_user_invalid_user(client: TestClient):
    register = client.post(
        "/auth/register",
        json=FIRST_USER,
    )
    assert register.status_code == 201

    response = client.post(
        "/auth/login",
        data={"username": SECOND_USER["email"], "password": SECOND_USER["password"]},
    )
    assert response.status_code == 401

    error = response.json()["error"]
    assert error["code"] == "INVALID_CREDENTIALS"
    assert error["message"] == "Invalid email or password"


def test_get_current_user_info_success(client: TestClient):
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
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert data["email"] == FIRST_USER["email"]
    assert data["is_active"] is True

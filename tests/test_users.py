from app import schemas
from jose import jwt
from app.config import settings
import pytest


def test_create_user(client):
    response = client.post(
        "/users", json={"email": "hello123@gmail.com", "password": "password123"}
    )

    new_user = schemas.UserOut(**response.json())
    # print(type(new_user))
    assert new_user.email == "hello123@gmail.com"
    assert response.status_code == 201


def test_login_user(client, test_user):
    response = client.post(
        "/login",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    login_response = schemas.Token(**response.json())
    # print(login_response)
    # print(response.json())
    payload = jwt.decode(
        login_response.access_token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )
    id = payload.get("user_id")
    assert response.status_code == 200
    assert login_response.token_type == "bearer"
    assert id == test_user["id"]


@pytest.mark.parametrize(
    "email, password,status_code",
    [
        ("wrongemail@gmail.com", "test123", 403),
        ("test123@test.com", "wrongpassword", 403),
        ("wrongemail@gmail.com", "wrongpassword", 403),
        (None, "test123", 422),
        ("test123@test.com", None, 422),
    ],
)
def test_incorrect_login(client, test_user, email, password, status_code):
    response = client.post("/login", data={"username": email, "password": password})
    assert response.status_code == status_code

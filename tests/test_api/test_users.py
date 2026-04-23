import pytest
from httpx import AsyncClient

from decimal import Decimal

from tests.conftest import auth_header, login_user, create_test_user


@pytest.mark.anyio
async def test_create_user(client: AsyncClient):

    response = await client.post(
        "/users",
        json={"username":"test_user","email": "test@example.com", "password": "testpassword1"},
    )

    assert response.status_code == 201
    assert response.json()["role"] == "user"


@pytest.mark.anyio
async def test_create_user_validation_error(client: AsyncClient):

    response = await client.post(
        "/users",
        json={"email":"test@example.com"},
    )
    assert response.status_code == 422
    assert "username" in response.text
    assert "password" in response.text


@pytest.mark.anyio
async def test_create_user_with_same_email(client: AsyncClient):
    await client.post(
        "/users",
        json={"username":"test_user","email":"test@example.com", "password": "testpassword1"},
    )

    response = await client.post(
        "/users",
        json={"username":"test_user1","email":"test@example.com", "password": "testpassword1"},

    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_create_user_with_same_username(client: AsyncClient):
    await client.post(
        "/users",
        json={"username":"test_user","email":"test@example.com", "password": "testpassword1"},
    )

    response = await client.post(
        "/users",
        json={"username":"test_user","email":"test1@example.com", "password": "testpassword1"},

    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_create_user_with_short_password(client: AsyncClient):
    response = await client.post(
        "/users",
        json={"username":"test_user","email":"test@example.com", "password": "1"}
    )
    assert response.status_code == 422

@pytest.mark.anyio
async def test_create_user_with_invalid_email(client: AsyncClient):
    response = await client.post(
        "/users",
        json={"username":"test_user", "email":"4242142", "password": "testpassword1"}
    )

    assert response.status_code == 422

@pytest.mark.anyio
async def test_login_user(client: AsyncClient):
    await create_test_user(client, email="test@example.com", password="testpassword")

    response = await client.post(
        "/users/token",
        data={"username": "test@example.com", "password": "testpassword"}

    )

    assert response.status_code == 200
    assert response.json()["access_token"] is not None

@pytest.mark.anyio
async def test_login_user_with_invalid_password(client: AsyncClient):
    await create_test_user(client, password="testpassword1")
    response = await client.post(
        "/users/token",
        data={"username": "test@example.com", "password": "testpassword"}

    )

    assert response.status_code == 401

@pytest.mark.anyio
async def test_get_current_user(client: AsyncClient):
    await create_test_user(client, username="test_user", email="test@example.com", password="testpassword")
    token = await login_user(client, email="test@example.com", password="testpassword")
    headers = auth_header(token)

    response = await client.get(
        "users/me",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["username"] == "test_user"
    assert response.json()["email"] == "test@example.com"
    assert response.json()["role"] == "user"
    assert response.json()["is_active"] is True

@pytest.mark.anyio
async def test_delete_user(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.delete(
        "users/me",
        headers=headers
    )

    assert response.status_code == 204

    response = await client.get(
        "users/me",
        headers=headers
    )

    assert response.status_code == 401
import pytest
from httpx import AsyncClient

from decimal import Decimal

from tests.conftest import auth_header, login_user, create_test_user

@pytest.mark.anyio
async def test_create_wallet(client:AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)


    response = await client.post(
        "/wallets",
        json={"name": "test_wallet", "currency": "usd"},
        headers = headers
    )


    assert response.status_code == 200
    assert response.json()["name"] == "test_wallet"
    assert response.json()["currency"] == "usd"
    assert response.json()["balance"] == "0"


@pytest.mark.anyio
async def test_create_wallet_unauthorized(client: AsyncClient):
    response = await client.post(
        "/wallets",
        json={"name": "test_wallet", "currency": "usd"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.anyio
async def test_create_duplicate_wallet(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    await client.post(
        "/wallets",
        json={"name": "test_wallet", "currency": "usd"},
        headers=headers
    )

    response = await client.post(
        "/wallets",
        json={"name": "test_wallet", "currency": "usd"},
        headers=headers
    )

    assert response.status_code == 400

@pytest.mark.anyio
async def test_create_same_wallet_different_users(client: AsyncClient):
    await create_test_user(client)
    token1 = await login_user(client)
    headers1 = auth_header(token1)

    await client.post(
        "/wallets",
        json={"name": "test_wallet", "currency": "usd"},
        headers=headers1
    )

    await create_test_user(client, username="test_user2", email="test2@example.com")
    token2 = await login_user(client, email="test2@example.com")
    headers2 = auth_header(token2)
    response = await client.post(
        "/wallets",
        json={"name": "test_wallet", "currency": "usd"},
        headers=headers2
    )

    assert response.status_code == 200
    assert response.json()["name"] == "test_wallet"
    assert response.json()["currency"] == "usd"



@pytest.mark.anyio
async def test_create_wallet_with_empty_name(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.post(
        "/wallets",
        json={"name": "", "currency": "usd"},
        headers=headers
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_wallet_with_long_name(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.post(
        "/wallets",
        json={"name": f"{"a"*128}", "currency": "usd"},
        headers=headers
    )
    assert response.status_code == 422




@pytest.mark.anyio
async def test_get_wallet(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    await client.post(
        "/wallets",
        json={"name": "test_wallet", "currency": "usd"},
        headers=headers
    )

    response = await client.get(
        "/wallets/test_wallet",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == "test_wallet"
    assert response.json()["currency"] == "usd"
    assert response.json()["balance"] == "0"

@pytest.mark.anyio
async def test_get_non_existent_wallet(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.get(
        "/wallets/test_wallet",
        headers=headers
    )

    assert response.status_code == 404




@pytest.mark.anyio
async def test_delete_wallet(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    await client.post(
        "/wallets",
        json={"name": "test_wallet", "currency": "usd"},
        headers=headers
    )

    response = await client.delete(
        "/wallets/test_wallet",
        headers=headers
    )

    assert response.status_code == 204

@pytest.mark.anyio
async def test_delete_non_existent_wallet(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)
    response = await client.delete(
        "/wallets/test_wallet",
        headers=headers
    )

    assert response.status_code == 404

@pytest.mark.anyio
async def test_delete_wallet_already_deleted(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    await client.post(
        "/wallets",
        json={"name": "test_wallet", "currency": "usd"},
        headers=headers
    )

    await client.delete(
        "/wallets/test_wallet",
        headers=headers
    )

    response = await client.delete(
        "/wallets/test_wallet",
        headers=headers
    )

    assert response.status_code == 404

@pytest.mark.anyio
async def test_update_wallet(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    await client.post(
        "/wallets",
        json={"name": "test_wallet", "currency": "usd"},
        headers=headers
    )

    response = await client.patch(
        "/wallets",
        json={"old_name": "test_wallet", "new_name": "new_wallet"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "new_wallet"

@pytest.mark.anyio
async def test_get_total_balance(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    await client.post(
        "/wallets",
        json={"name": "test_wallet", "currency": "usd"},
        headers=headers
    )

    response = await client.get(
        "/wallets/balance",
        headers=headers
    )

    assert response.status_code == 200
    assert Decimal(response.json()["balance"]).is_zero()
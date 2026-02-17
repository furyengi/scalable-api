import pytest


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post("/api/v1/auth/register", json={"email": "new@example.com", "username": "newuser", "password": "Password123"})
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"


@pytest.mark.asyncio
async def test_login(client, test_user):
    response = await client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "Password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    response = await client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "wrongpass"})
    assert response.status_code == 401

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        res = await client.post("/auth/register", json={
            "email": "newuser@test.com",
            "password": "SecurePass123!"
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        res = await client.post("/auth/register", json={
            "email": test_user.email,
            "password": "SecurePass123!"
        })
        assert res.status_code == 400
        assert "registrado" in res.json()["detail"]

    async def test_register_invalid_email(self, client: AsyncClient):
        res = await client.post("/auth/register", json={
            "email": "notanemail",
            "password": "SecurePass123!"
        })
        assert res.status_code == 422

    async def test_register_missing_password(self, client: AsyncClient):
        res = await client.post("/auth/register", json={
            "email": "test@test.com"
        })
        assert res.status_code == 422

    async def test_register_empty_password(self, client: AsyncClient):
        res = await client.post("/auth/register", json={
            "email": "test@test.com",
            "password": ""
        })
        assert res.status_code == 422

    async def test_register_sql_injection_email(self, client: AsyncClient):
        res = await client.post("/auth/register", json={
            "email": "'; DROP TABLE users; --@test.com",
            "password": "SecurePass123!"
        })
        assert res.status_code == 422

    async def test_register_xss_in_email(self, client: AsyncClient):
        res = await client.post("/auth/register", json={
            "email": "<script>alert('xss')</script>@test.com",
            "password": "SecurePass123!"
        })
        assert res.status_code == 422


class TestLogin:
    async def test_login_success(self, client: AsyncClient, test_user):
        res = await client.post("/auth/login", json={
            "email": test_user.email,
            "password": "TestPass123!"
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        res = await client.post("/auth/login", json={
            "email": test_user.email,
            "password": "WrongPassword!"
        })
        assert res.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        res = await client.post("/auth/login", json={
            "email": "nobody@test.com",
            "password": "SomePass123!"
        })
        assert res.status_code == 401

    async def test_login_paused_account(self, client: AsyncClient, test_user, db: AsyncSession):
        test_user.is_active = False
        await db.commit()
        res = await client.post("/auth/login", json={
            "email": test_user.email,
            "password": "TestPass123!"
        })
        assert res.status_code == 403

    async def test_login_sql_injection(self, client: AsyncClient):
        res = await client.post("/auth/login", json={
            "email": "' OR '1'='1",
            "password": "' OR '1'='1"
        })
        assert res.status_code == 422

    async def test_login_missing_fields(self, client: AsyncClient):
        res = await client.post("/auth/login", json={})
        assert res.status_code == 422


class TestMe:
    async def test_me_authenticated(self, client: AsyncClient, auth_headers, test_user):
        res = await client.get("/auth/me", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["email"] == test_user.email
        assert "password" not in data

    async def test_me_no_token(self, client: AsyncClient):
        res = await client.get("/auth/me")
        assert res.status_code == 403

    async def test_me_invalid_token(self, client: AsyncClient):
        res = await client.get("/auth/me", headers={
            "Authorization": "Bearer invalidtoken123"
        })
        assert res.status_code == 401

    async def test_me_malformed_token(self, client: AsyncClient):
        res = await client.get("/auth/me", headers={
            "Authorization": "NotBearer token"
        })
        assert res.status_code == 403

    async def test_me_empty_token(self, client: AsyncClient):
        res = await client.get("/auth/me", headers={
            "Authorization": "Bearer "
        })
        assert res.status_code == 403

    async def test_me_does_not_expose_password(self, client: AsyncClient, auth_headers):
        res = await client.get("/auth/me", headers=auth_headers)
        assert res.status_code == 200
        assert "password" not in res.json()
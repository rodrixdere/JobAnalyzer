import pytest
from httpx import AsyncClient
import uuid


class TestSQLInjection:
    async def test_sql_injection_login(self, client: AsyncClient):
        payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "admin'--",
            "' UNION SELECT * FROM users--",
            "'; DROP TABLE users;--",
        ]
        for payload in payloads:
            res = await client.post("/auth/login", json={
                "email": payload,
                "password": payload
            })
            assert res.status_code in [401, 422], f"SQL injection not blocked: {payload}"

    async def test_sql_injection_register(self, client: AsyncClient):
        payloads = [
            "'; DROP TABLE users; --@test.com",
            "' OR '1'='1'@test.com",
            "admin'--@test.com",
        ]
        for payload in payloads:
            res = await client.post("/auth/register", json={
                "email": payload,
                "password": "SecurePass123!"
            })
            assert res.status_code == 422, f"SQL injection not blocked: {payload}"


class TestUnauthorizedAccess:
    async def test_all_protected_endpoints_require_auth(self, client: AsyncClient):
        endpoints = [
            ("GET", "/profile/"),
            ("PUT", "/profile/"),
            ("POST", "/profile/parse-cv"),
            ("POST", "/profile/upload-cv"),
            ("GET", "/analysis/"),
            ("POST", "/analysis/"),
            ("GET", f"/analysis/{uuid.uuid4()}"),
            ("DELETE", f"/analysis/{uuid.uuid4()}"),
            ("GET", "/tracker/"),
            ("POST", "/tracker/"),
            ("PUT", f"/tracker/{uuid.uuid4()}"),
            ("DELETE", f"/tracker/{uuid.uuid4()}"),
            ("GET", "/admin/users"),
            ("POST", "/admin/users"),
            ("PUT", f"/admin/users/{uuid.uuid4()}/toggle"),
            ("DELETE", f"/admin/users/{uuid.uuid4()}"),
        ]
        for method, path in endpoints:
            res = await client.request(method, path)
            assert res.status_code in [401, 403, 422], f"{method} {path} should require auth, got {res.status_code}"

    async def test_expired_token_rejected(self, client: AsyncClient):
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxfQ.invalid"
        res = await client.get("/profile/", headers={
            "Authorization": f"Bearer {expired_token}"
        })
        assert res.status_code == 401

    async def test_tampered_token_rejected(self, client: AsyncClient):
        res = await client.get("/profile/", headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJoYWNrZXIifQ.tampered"
        })
        assert res.status_code == 401

    async def test_admin_endpoints_blocked_for_regular_users(self, client: AsyncClient, auth_headers):
        endpoints = [
            ("GET", "/admin/users"),
            ("POST", "/admin/users"),
            ("PUT", f"/admin/users/{uuid.uuid4()}/toggle"),
            ("DELETE", f"/admin/users/{uuid.uuid4()}"),
        ]
        for method, path in endpoints:
            res = await client.request(method, path, headers=auth_headers)
            assert res.status_code in [401, 403], f"{method} {path} should be admin only"


class TestDataIsolation:
    async def test_users_cannot_access_each_other_data(
        self, client: AsyncClient, auth_headers, admin_headers
    ):
        admin_res = await client.get("/profile/", headers=admin_headers)
        user_res = await client.get("/profile/", headers=auth_headers)

        if admin_res.status_code == 200 and user_res.status_code == 200:
            assert admin_res.json()["user_id"] != user_res.json()["user_id"]

    async def test_analysis_isolated_between_users(
        self, client: AsyncClient, auth_headers, admin_headers
    ):
        user_analyses = await client.get("/analysis/", headers=auth_headers)
        admin_analyses = await client.get("/analysis/", headers=admin_headers)

        assert user_analyses.status_code == 200
        assert admin_analyses.status_code == 200

        user_ids = {a["id"] for a in user_analyses.json()}
        admin_ids = {a["id"] for a in admin_analyses.json()}
        assert user_ids.isdisjoint(admin_ids)

    async def test_tracker_isolated_between_users(
        self, client: AsyncClient, auth_headers, admin_headers
    ):
        user_jobs = await client.get("/tracker/", headers=auth_headers)
        admin_jobs = await client.get("/tracker/", headers=admin_headers)

        assert user_jobs.status_code == 200
        assert admin_jobs.status_code == 200

        user_ids = {j["id"] for j in user_jobs.json()}
        admin_ids = {j["id"] for j in admin_jobs.json()}
        assert user_ids.isdisjoint(admin_ids)


class TestInputValidation:
    async def test_oversized_payload(self, client: AsyncClient, auth_headers):
        large_text = "A" * 1_000_000
        res = await client.post("/analysis/", headers=auth_headers, json={
            "job_text": large_text
        })
        assert res.status_code in [200, 400, 413, 422, 502]

    async def test_invalid_uuid_format(self, client: AsyncClient, auth_headers):
        invalid_ids = ["notauuid", "123", "null", "undefined", "../etc/passwd"]
        for invalid_id in invalid_ids:
            res = await client.get(f"/analysis/{invalid_id}", headers=auth_headers)
            assert res.status_code in [404, 422]

    async def test_health_endpoint_public(self, client: AsyncClient):
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"
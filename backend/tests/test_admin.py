import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import hash_password, create_access_token
import uuid


@pytest.fixture
async def target_user(db: AsyncSession):
    user = User(
        id=uuid.uuid4(),
        email=f"target_{uuid.uuid4().hex[:8]}@test.com",
        password=hash_password("TargetPass123!"),
        is_active=True,
        is_admin=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    yield user
    try:
        await db.delete(user)
        await db.commit()
    except Exception:
        pass


class TestAdminListUsers:
    async def test_list_users_as_admin(self, client: AsyncClient, admin_headers):
        res = await client.get("/admin/users", headers=admin_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    async def test_list_users_as_regular_user(self, client: AsyncClient, auth_headers):
        res = await client.get("/admin/users", headers=auth_headers)
        assert res.status_code in [401, 403]

    async def test_list_users_no_auth(self, client: AsyncClient):
        res = await client.get("/admin/users")
        assert res.status_code in [401, 403]

    async def test_list_users_does_not_expose_passwords(self, client: AsyncClient, admin_headers):
        res = await client.get("/admin/users", headers=admin_headers)
        assert res.status_code == 200
        for user in res.json():
            assert "password" not in user

    async def test_list_users_invalid_token(self, client: AsyncClient):
        res = await client.get("/admin/users", headers={
            "Authorization": "Bearer faketoken"
        })
        assert res.status_code == 401


class TestAdminCreateUser:
    async def test_create_user_as_admin(self, client: AsyncClient, admin_headers):
        res = await client.post("/admin/users", headers=admin_headers, json={
            "email": f"newuser_{uuid.uuid4().hex[:8]}@test.com",
            "password": "NewPass123!",
            "is_admin": False,
        })
        assert res.status_code == 200
        data = res.json()
        assert "email" in data
        assert "password" not in data

    async def test_create_user_as_regular_user(self, client: AsyncClient, auth_headers):
        res = await client.post("/admin/users", headers=auth_headers, json={
            "email": "hack@test.com",
            "password": "HackPass123!",
            "is_admin": True,
        })
        assert res.status_code in [401, 403]

    async def test_create_user_no_auth(self, client: AsyncClient):
        res = await client.post("/admin/users", json={
            "email": "hack@test.com",
            "password": "HackPass123!",
        })
        assert res.status_code in [401, 403]

    async def test_create_user_duplicate_email(self, client: AsyncClient, admin_headers, target_user):
        res = await client.post("/admin/users", headers=admin_headers, json={
            "email": target_user.email,
            "password": "NewPass123!",
            "is_admin": False,
        })
        assert res.status_code == 400

    async def test_create_user_invalid_email(self, client: AsyncClient, admin_headers):
        res = await client.post("/admin/users", headers=admin_headers, json={
            "email": "notanemail",
            "password": "NewPass123!",
            "is_admin": False,
        })
        assert res.status_code == 422

    async def test_regular_user_cannot_create_admin(self, client: AsyncClient, auth_headers):
        res = await client.post("/admin/users", headers=auth_headers, json={
            "email": "fakeadmin@test.com",
            "password": "FakePass123!",
            "is_admin": True,
        })
        assert res.status_code in [401, 403]


class TestAdminToggleUser:
    async def test_toggle_user_pause(self, client: AsyncClient, admin_headers, target_user):
        res = await client.put(f"/admin/users/{target_user.id}/toggle", headers=admin_headers, json={
            "is_active": False
        })
        assert res.status_code == 200
        assert res.json()["is_active"] is False

    async def test_toggle_user_reactivate(self, client: AsyncClient, admin_headers, target_user, db: AsyncSession):
        target_user.is_active = False
        await db.commit()

        res = await client.put(f"/admin/users/{target_user.id}/toggle", headers=admin_headers, json={
            "is_active": True
        })
        assert res.status_code == 200
        assert res.json()["is_active"] is True

    async def test_toggle_as_regular_user(self, client: AsyncClient, auth_headers, target_user):
        res = await client.put(f"/admin/users/{target_user.id}/toggle", headers=auth_headers, json={
            "is_active": False
        })
        assert res.status_code in [401, 403]

    async def test_toggle_no_auth(self, client: AsyncClient, target_user):
        res = await client.put(f"/admin/users/{target_user.id}/toggle", json={
            "is_active": False
        })
        assert res.status_code in [401, 403]

    async def test_admin_cannot_pause_self(self, client: AsyncClient, admin_headers, test_admin):
        res = await client.put(f"/admin/users/{test_admin.id}/toggle", headers=admin_headers, json={
            "is_active": False
        })
        assert res.status_code == 400

    async def test_toggle_nonexistent_user(self, client: AsyncClient, admin_headers):
        fake_id = uuid.uuid4()
        res = await client.put(f"/admin/users/{fake_id}/toggle", headers=admin_headers, json={
            "is_active": False
        })
        assert res.status_code == 404

    async def test_paused_user_cannot_login(self, client: AsyncClient, admin_headers, target_user, db: AsyncSession):
        target_user.is_active = False
        await db.commit()

        res = await client.post("/auth/login", json={
            "email": target_user.email,
            "password": "TargetPass123!"
        })
        assert res.status_code in [401, 403]

    async def test_paused_user_cannot_access_endpoints(self, client: AsyncClient, db: AsyncSession, target_user):
        token = create_access_token(str(target_user.id))
        target_user.is_active = False
        await db.commit()

        res = await client.get("/profile/", headers={
            "Authorization": f"Bearer {token}"
        })
        assert res.status_code in [401, 403]


class TestAdminDeleteUser:
    async def test_delete_user_as_admin(self, client: AsyncClient, admin_headers, db: AsyncSession):
        user_to_delete = User(
            id=uuid.uuid4(),
            email=f"delete_{uuid.uuid4().hex[:8]}@test.com",
            password=hash_password("DeletePass123!"),
            is_active=True,
            is_admin=False,
        )
        db.add(user_to_delete)
        await db.commit()

        res = await client.delete(f"/admin/users/{user_to_delete.id}", headers=admin_headers)
        assert res.status_code == 204

    async def test_delete_user_as_regular_user(self, client: AsyncClient, auth_headers, target_user):
        res = await client.delete(f"/admin/users/{target_user.id}", headers=auth_headers)
        assert res.status_code in [401, 403]

    async def test_delete_user_no_auth(self, client: AsyncClient, target_user):
        res = await client.delete(f"/admin/users/{target_user.id}")
        assert res.status_code in [401, 403]

    async def test_admin_cannot_delete_self(self, client: AsyncClient, admin_headers, test_admin):
        res = await client.delete(f"/admin/users/{test_admin.id}", headers=admin_headers)
        assert res.status_code == 400

    async def test_delete_nonexistent_user(self, client: AsyncClient, admin_headers):
        fake_id = uuid.uuid4()
        res = await client.delete(f"/admin/users/{fake_id}", headers=admin_headers)
        assert res.status_code == 404
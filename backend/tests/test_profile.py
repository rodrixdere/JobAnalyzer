import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.profile import UserProfile
from app.models.user import User
from app.core.security import hash_password, create_access_token
import uuid


@pytest.fixture
async def test_profile(db: AsyncSession, test_user: User):
    profile = UserProfile(
        id=uuid.uuid4(),
        user_id=test_user.id,
        raw_text="Sample CV text",
        full_name="Test User",
        professional_title="Software Engineer",
        email="test@test.com",
        skills=["Python", "FastAPI"],
        experience=[{"title": "Dev", "company": "Corp", "years": 2.0}],
        projects=[],
        education=[],
        languages=["Spanish"],
        links={"github": None, "linkedin": None, "portfolio": None},
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    yield profile
    await db.delete(profile)
    await db.commit()


class TestGetProfile:
    async def test_get_profile_success(self, client: AsyncClient, auth_headers, test_profile):
        res = await client.get("/profile/", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["full_name"] == "Test User"
        assert data["professional_title"] == "Software Engineer"
        assert "Python" in data["skills"]

    async def test_get_profile_not_found(self, client: AsyncClient, auth_headers):
        res = await client.get("/profile/", headers=auth_headers)
        assert res.status_code == 404

    async def test_get_profile_no_auth(self, client: AsyncClient):
        res = await client.get("/profile/")
        assert res.status_code in [401, 403]

    async def test_get_profile_invalid_token(self, client: AsyncClient):
        res = await client.get("/profile/", headers={
            "Authorization": "Bearer faketoken"
        })
        assert res.status_code == 401

    async def test_cannot_access_other_user_profile(self, client: AsyncClient, db: AsyncSession, test_profile):
        other_user = User(
            id=uuid.uuid4(),
            email=f"other_{uuid.uuid4().hex[:8]}@test.com",
            password=hash_password("OtherPass123!"),
            is_active=True,
            is_admin=False,
        )
        db.add(other_user)
        await db.commit()

        other_token = create_access_token(str(other_user.id))
        res = await client.get("/profile/", headers={
            "Authorization": f"Bearer {other_token}"
        })
        assert res.status_code == 404

        await db.delete(other_user)
        await db.commit()


class TestParseCV:
    async def test_parse_cv_no_auth(self, client: AsyncClient):
        res = await client.post("/profile/parse-cv", json={"text": "CV content"})
        assert res.status_code in [401, 403]

    async def test_parse_cv_missing_text(self, client: AsyncClient, auth_headers):
        res = await client.post("/profile/parse-cv", json={})
        assert res.status_code == 400

    async def test_parse_cv_empty_text(self, client: AsyncClient, auth_headers):
        res = await client.post("/profile/parse-cv", json={"text": ""})
        assert res.status_code == 400

    async def test_parse_cv_sql_injection(self, client: AsyncClient, auth_headers):
        res = await client.post("/profile/parse-cv", json={
            "text": "'; DROP TABLE user_profiles; --"
        })
        assert res.status_code in [200, 502]

    async def test_parse_cv_xss_attempt(self, client: AsyncClient, auth_headers):
        res = await client.post("/profile/parse-cv", json={
            "text": "<script>alert('xss')</script>"
        })
        assert res.status_code in [200, 502]


class TestUpdateProfile:
    async def test_update_profile_success(self, client: AsyncClient, auth_headers, test_profile):
        res = await client.put("/profile/", headers=auth_headers, json={
            "skills": ["Python", "FastAPI", "React"],
            "languages": ["Spanish", "English"]
        })
        assert res.status_code == 200
        data = res.json()
        assert "React" in data["skills"]
        assert "English" in data["languages"]

    async def test_update_profile_no_auth(self, client: AsyncClient):
        res = await client.put("/profile/", json={"skills": ["Python"]})
        assert res.status_code in [401, 403]

    async def test_update_profile_not_found(self, client: AsyncClient, auth_headers):
        res = await client.put("/profile/", headers=auth_headers, json={
            "skills": ["Python"]
        })
        assert res.status_code == 404

    async def test_update_profile_invalid_experience(self, client: AsyncClient, auth_headers, test_profile):
        res = await client.put("/profile/", headers=auth_headers, json={
            "experience": [{"title": "Dev"}]
        })
        assert res.status_code == 422

    async def test_update_profile_sql_injection_in_skills(self, client: AsyncClient, auth_headers, test_profile):
        res = await client.put("/profile/", headers=auth_headers, json={
            "skills": ["'; DROP TABLE user_profiles; --"]
        })
        assert res.status_code == 200
        data = res.json()
        assert data["skills"] == ["'; DROP TABLE user_profiles; --"]


class TestUploadCV:
    async def test_upload_cv_no_auth(self, client: AsyncClient):
        res = await client.post("/profile/upload-cv", files={
            "file": ("test.pdf", b"fake pdf content", "application/pdf")
        })
        assert res.status_code in [401, 403]

    async def test_upload_cv_invalid_format(self, client: AsyncClient, auth_headers):
        res = await client.post("/profile/upload-cv", headers=auth_headers, files={
            "file": ("test.txt", b"some text", "text/plain")
        })
        assert res.status_code == 400

    async def test_upload_cv_empty_file(self, client: AsyncClient, auth_headers):
        res = await client.post("/profile/upload-cv", headers=auth_headers, files={
            "file": ("test.pdf", b"", "application/pdf")
        })
        assert res.status_code == 400
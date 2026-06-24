import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.analysis import Analysis
from app.models.profile import UserProfile
from app.models.user import User
from app.core.security import hash_password, create_access_token
import uuid


@pytest.fixture
async def test_profile(db: AsyncSession, test_user: User):
    profile = UserProfile(
        id=uuid.uuid4(),
        user_id=test_user.id,
        raw_text="Fullstack developer with React and Python experience",
        full_name="Test User",
        professional_title="Software Engineer",
        email="test@test.com",
        skills=["React", "Python", "PostgreSQL"],
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


@pytest.fixture
async def test_analysis(db: AsyncSession, test_user: User):
    analysis = Analysis(
        id=uuid.uuid4(),
        user_id=test_user.id,
        job_title="Frontend Developer",
        company="TechCorp",
        job_text="We need a React developer",
        required_skills=["React", "TypeScript"],
        matching_skills=["React"],
        missing_skills=["TypeScript"],
        match_score=60,
        summary="Good match for React, missing TypeScript",
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    yield analysis
    await db.delete(analysis)
    await db.commit()


class TestCreateAnalysis:
    async def test_create_analysis_no_auth(self, client: AsyncClient):
        res = await client.post("/analysis/", json={"job_text": "We need a React developer"})
        assert res.status_code in [401, 403]

    async def test_create_analysis_no_profile(self, client: AsyncClient, auth_headers):
        res = await client.post("/analysis/", json={"job_text": "We need a React developer"})
        assert res.status_code == 400
        assert "perfil" in res.json()["detail"].lower()

    async def test_create_analysis_missing_job_text(self, client: AsyncClient, auth_headers, test_profile):
        res = await client.post("/analysis/", headers=auth_headers, json={})
        assert res.status_code == 422

    async def test_create_analysis_empty_job_text(self, client: AsyncClient, auth_headers, test_profile):
        res = await client.post("/analysis/", headers=auth_headers, json={"job_text": ""})
        assert res.status_code == 422

    async def test_create_analysis_sql_injection(self, client: AsyncClient, auth_headers, test_profile):
        res = await client.post("/analysis/", headers=auth_headers, json={
            "job_text": "'; DROP TABLE analyses; --"
        })
        assert res.status_code in [200, 502]

    async def test_create_analysis_invalid_token(self, client: AsyncClient):
        res = await client.post("/analysis/", headers={
            "Authorization": "Bearer faketoken"
        }, json={"job_text": "We need a React developer"})
        assert res.status_code == 401


class TestListAnalysis:
    async def test_list_analysis_success(self, client: AsyncClient, auth_headers, test_analysis):
        res = await client.get("/analysis/", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        ids = [a["id"] for a in data]
        assert str(test_analysis.id) in ids

    async def test_list_analysis_no_auth(self, client: AsyncClient):
        res = await client.get("/analysis/")
        assert res.status_code in [401, 403]

    async def test_list_analysis_empty(self, client: AsyncClient, auth_headers):
        res = await client.get("/analysis/", headers=auth_headers)
        assert res.status_code == 200
        assert res.json() == []

    async def test_list_analysis_only_own(self, client: AsyncClient, db: AsyncSession, test_analysis):
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
        res = await client.get("/analysis/", headers={
            "Authorization": f"Bearer {other_token}"
        })
        assert res.status_code == 200
        ids = [a["id"] for a in res.json()]
        assert str(test_analysis.id) not in ids

        await db.delete(other_user)
        await db.commit()


class TestGetAnalysis:
    async def test_get_analysis_success(self, client: AsyncClient, auth_headers, test_analysis):
        res = await client.get(f"/analysis/{test_analysis.id}", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == str(test_analysis.id)
        assert data["job_title"] == "Frontend Developer"
        assert data["match_score"] == 60

    async def test_get_analysis_no_auth(self, client: AsyncClient, test_analysis):
        res = await client.get(f"/analysis/{test_analysis.id}")
        assert res.status_code in [401, 403]

    async def test_get_analysis_not_found(self, client: AsyncClient, auth_headers):
        fake_id = uuid.uuid4()
        res = await client.get(f"/analysis/{fake_id}", headers=auth_headers)
        assert res.status_code == 404

    async def test_get_analysis_other_user_forbidden(self, client: AsyncClient, db: AsyncSession, test_analysis):
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
        res = await client.get(f"/analysis/{test_analysis.id}", headers={
            "Authorization": f"Bearer {other_token}"
        })
        assert res.status_code == 404

        await db.delete(other_user)
        await db.commit()

    async def test_get_analysis_invalid_uuid(self, client: AsyncClient, auth_headers):
        res = await client.get("/analysis/notauuid", headers=auth_headers)
        assert res.status_code == 422


class TestDeleteAnalysis:
    async def test_delete_analysis_success(self, client: AsyncClient, auth_headers, db: AsyncSession, test_user: User):
        analysis = Analysis(
            id=uuid.uuid4(),
            user_id=test_user.id,
            job_title="Dev",
            company="Corp",
            job_text="Job text",
            required_skills=[],
            matching_skills=[],
            missing_skills=[],
            match_score=50,
            summary="Summary",
        )
        db.add(analysis)
        await db.commit()

        res = await client.delete(f"/analysis/{analysis.id}", headers=auth_headers)
        assert res.status_code == 204

        res2 = await client.get(f"/analysis/{analysis.id}", headers=auth_headers)
        assert res2.status_code == 404

    async def test_delete_analysis_no_auth(self, client: AsyncClient, test_analysis):
        res = await client.delete(f"/analysis/{test_analysis.id}")
        assert res.status_code in [401, 403]

    async def test_delete_analysis_not_found(self, client: AsyncClient, auth_headers):
        fake_id = uuid.uuid4()
        res = await client.delete(f"/analysis/{fake_id}", headers=auth_headers)
        assert res.status_code == 404

    async def test_delete_analysis_other_user_forbidden(self, client: AsyncClient, db: AsyncSession, test_analysis):
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
        res = await client.delete(f"/analysis/{test_analysis.id}", headers={
            "Authorization": f"Bearer {other_token}"
        })
        assert res.status_code == 404

        await db.delete(other_user)
        await db.commit()

    async def test_delete_analysis_invalid_uuid(self, client: AsyncClient, auth_headers):
        res = await client.delete("/analysis/notauuid", headers=auth_headers)
        assert res.status_code == 422
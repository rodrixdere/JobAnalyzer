import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tracker import JobApplication
from app.models.user import User
from app.core.security import hash_password, create_access_token
import uuid


@pytest.fixture
async def test_job(db: AsyncSession, test_user: User):
    job = JobApplication(
        id=uuid.uuid4(),
        user_id=test_user.id,
        job_title="Frontend Developer",
        company="TechCorp",
        status="Applied",
        type="Remote",
        keywords=["React", "TypeScript"],
        link="https://techcorp.com/jobs/1",
        notes="Looks interesting",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    yield job
    try:
        await db.delete(job)
        await db.commit()
    except Exception:
        pass


class TestListTracker:
    async def test_list_jobs_success(self, client: AsyncClient, auth_headers, test_job):
        res = await client.get("/tracker/", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        ids = [j["id"] for j in data]
        assert str(test_job.id) in ids

    async def test_list_jobs_no_auth(self, client: AsyncClient):
        res = await client.get("/tracker/")
        assert res.status_code in [401, 403]

    async def test_list_jobs_empty(self, client: AsyncClient, auth_headers):
        res = await client.get("/tracker/", headers=auth_headers)
        assert res.status_code == 200
        assert res.json() == []

    async def test_list_jobs_only_own(self, client: AsyncClient, db: AsyncSession, test_job):
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
        res = await client.get("/tracker/", headers={
            "Authorization": f"Bearer {other_token}"
        })
        assert res.status_code == 200
        ids = [j["id"] for j in res.json()]
        assert str(test_job.id) not in ids

        await db.delete(other_user)
        await db.commit()


class TestCreateTracker:
    async def test_create_job_success(self, client: AsyncClient, auth_headers):
        res = await client.post("/tracker/", headers=auth_headers, json={
            "job_title": "Backend Developer",
            "company": "StartupXYZ",
            "status": "Inbox",
            "type": "Remote",
            "keywords": ["Python", "FastAPI"],
            "link": "https://startupxyz.com/jobs/1",
        })
        assert res.status_code == 200
        data = res.json()
        assert data["job_title"] == "Backend Developer"
        assert data["company"] == "StartupXYZ"
        assert data["status"] == "Inbox"

    async def test_create_job_no_auth(self, client: AsyncClient):
        res = await client.post("/tracker/", json={
            "job_title": "Dev",
            "company": "Corp",
        })
        assert res.status_code in [401, 403]

    async def test_create_job_missing_required_fields(self, client: AsyncClient, auth_headers):
        res = await client.post("/tracker/", headers=auth_headers, json={
            "job_title": "Dev"
        })
        assert res.status_code == 422

    async def test_create_job_sql_injection_title(self, client: AsyncClient, auth_headers):
        res = await client.post("/tracker/", headers=auth_headers, json={
            "job_title": "'; DROP TABLE job_applications; --",
            "company": "Corp",
        })
        assert res.status_code == 200
        assert res.json()["job_title"] == "'; DROP TABLE job_applications; --"

    async def test_create_job_xss_in_notes(self, client: AsyncClient, auth_headers):
        res = await client.post("/tracker/", headers=auth_headers, json={
            "job_title": "Dev",
            "company": "Corp",
            "notes": "<script>alert('xss')</script>",
        })
        assert res.status_code == 200
        assert res.json()["notes"] == "<script>alert('xss')</script>"


class TestUpdateTracker:
    async def test_update_job_success(self, client: AsyncClient, auth_headers, test_job):
        res = await client.put(f"/tracker/{test_job.id}", headers=auth_headers, json={
            "status": "Interview",
            "notes": "Got a call back"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "Interview"
        assert data["notes"] == "Got a call back"

    async def test_update_job_no_auth(self, client: AsyncClient, test_job):
        res = await client.put(f"/tracker/{test_job.id}", json={"status": "Interview"})
        assert res.status_code in [401, 403]

    async def test_update_job_not_found(self, client: AsyncClient, auth_headers):
        fake_id = uuid.uuid4()
        res = await client.put(f"/tracker/{fake_id}", headers=auth_headers, json={
            "status": "Interview"
        })
        assert res.status_code == 404

    async def test_update_job_other_user_forbidden(self, client: AsyncClient, db: AsyncSession, test_job):
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
        res = await client.put(f"/tracker/{test_job.id}", headers={
            "Authorization": f"Bearer {other_token}"
        }, json={"status": "Interview"})
        assert res.status_code == 404

        await db.delete(other_user)
        await db.commit()

    async def test_update_job_invalid_uuid(self, client: AsyncClient, auth_headers):
        res = await client.put("/tracker/notauuid", headers=auth_headers, json={
            "status": "Interview"
        })
        assert res.status_code == 422


class TestDeleteTracker:
    async def test_delete_job_success(self, client: AsyncClient, auth_headers, db: AsyncSession, test_user: User):
        job = JobApplication(
            id=uuid.uuid4(),
            user_id=test_user.id,
            job_title="Dev",
            company="Corp",
            status="Inbox",
            keywords=[],
        )
        db.add(job)
        await db.commit()

        res = await client.delete(f"/tracker/{job.id}", headers=auth_headers)
        assert res.status_code == 204

        res2 = await client.get("/tracker/", headers=auth_headers)
        ids = [j["id"] for j in res2.json()]
        assert str(job.id) not in ids

    async def test_delete_job_no_auth(self, client: AsyncClient, test_job):
        res = await client.delete(f"/tracker/{test_job.id}")
        assert res.status_code in [401, 403]

    async def test_delete_job_not_found(self, client: AsyncClient, auth_headers):
        fake_id = uuid.uuid4()
        res = await client.delete(f"/tracker/{fake_id}", headers=auth_headers)
        assert res.status_code == 404

    async def test_delete_job_other_user_forbidden(self, client: AsyncClient, db: AsyncSession, test_job):
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
        res = await client.delete(f"/tracker/{test_job.id}", headers={
            "Authorization": f"Bearer {other_token}"
        })
        assert res.status_code == 404

        await db.delete(other_user)
        await db.commit()

    async def test_delete_job_invalid_uuid(self, client: AsyncClient, auth_headers):
        res = await client.delete("/tracker/notauuid", headers=auth_headers)
        assert res.status_code == 422
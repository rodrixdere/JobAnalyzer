import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import pool
from app.main import app
from app.db.session import get_db
from app.db.base import Base
from app.models.user import User
from app.models.profile import UserProfile
from app.models.analysis import Analysis
from app.models.tracker import JobApplication
from app.core.security import hash_password, create_access_token
from app.core.config import settings
import uuid

TEST_DB_URL = settings.DATABASE_URL.replace(
    settings.DATABASE_URL.split("/")[-1], "postgres_test"
)

engine_test = create_async_engine(
    settings.DATABASE_URL,
    poolclass=pool.NullPool,
    connect_args={"statement_cache_size": 0},
)

TestSessionLocal = sessionmaker(
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="function")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def db():
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def test_user(db: AsyncSession):
    user = User(
        id=uuid.uuid4(),
        email=f"test_{uuid.uuid4().hex[:8]}@test.com",
        password=hash_password("TestPass123!"),
        is_active=True,
        is_admin=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    yield user
    await db.delete(user)
    await db.commit()


@pytest_asyncio.fixture(scope="function")
async def test_admin(db: AsyncSession):
    admin = User(
        id=uuid.uuid4(),
        email=f"admin_{uuid.uuid4().hex[:8]}@test.com",
        password=hash_password("AdminPass123!"),
        is_active=True,
        is_admin=True,
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    yield admin
    await db.delete(admin)
    await db.commit()


@pytest_asyncio.fixture(scope="function")
async def user_token(test_user: User):
    return create_access_token(str(test_user.id))


@pytest_asyncio.fixture(scope="function")
async def admin_token(test_admin: User):
    return create_access_token(str(test_admin.id))


@pytest_asyncio.fixture(scope="function")
async def auth_headers(user_token: str):
    return {"Authorization": f"Bearer {user_token}"}


@pytest_asyncio.fixture(scope="function")
async def admin_headers(admin_token: str):
    return {"Authorization": f"Bearer {admin_token}"}
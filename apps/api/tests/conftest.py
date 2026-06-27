"""Test configuration and fixtures for Shouko-AI API.

IMPORTANT: Environment variables MUST be set before any project module imports
so that the Settings singleton is initialized with test-compatible values.
"""
import asyncio
import os

# ── Set test env vars BEFORE any project imports ──
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("APP_SECRET_KEY", "test-secret-key-for-ci-only-32chars!!")
os.environ.setdefault("OPENROUTER_API_KEY", "dummy-key")

# Now safe to import project modules (Settings() will see the env vars above)
import pytest
import pytest_asyncio
import httpx
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.config import settings
from core.database import get_db
from main import app
import uuid
from sqlalchemy import text
from core.database import Base
from models.user import User
import models  # Ensure all models are registered

TEST_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")
TEST_USER_EMAIL = "test@shouko-ai.app"

# Derive test database URL by replacing the target database name
test_db_url = settings.DATABASE_URL.rsplit("/", 1)[0] + "/shouko_test"

# Dedicated test engine with NullPool to prevent connection reuse issues
test_engine = create_async_engine(
    test_db_url,
    poolclass=NullPool,
    future=True
)

test_sessionmaker = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db(event_loop):
    # Ensure test database exists by connecting to the main database first
    admin_engine = create_async_engine(
        settings.DATABASE_URL,
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
        future=True
    )
    async with admin_engine.connect() as conn:
        try:
            await conn.execute(text("CREATE DATABASE shouko_test;"))
        except Exception:
            # Database already exists or other error
            pass
    await admin_engine.dispose()

    async with test_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
        await conn.run_sync(Base.metadata.create_all)

    async with test_sessionmaker() as session:
        default_user = User(
            id=TEST_USER_ID,
            email=TEST_USER_EMAIL,
            name="Test User",
            plan="free"
        )
        await session.merge(default_user)
        await session.commit()

    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop

@pytest.fixture(autouse=True)
def mock_rate_limit():
    """Prevent Redis-dependent rate limiter from blocking tests."""
    with patch("routers.chat.check_usage_limit", return_value=(True, None)), \
         patch("routers.papers.check_usage_limit", return_value=(True, None)), \
         patch("routers.artifacts.check_usage_limit", return_value=(True, None)), \
         patch("core.rate_limit.RateLimiter.is_rate_limited", return_value=False):
        yield

@pytest_asyncio.fixture
async def client():
    async def override_get_db():
        async with test_sessionmaker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
def auth_headers():
    return {"Authorization": "Bearer real-test-token"}

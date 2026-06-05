import asyncio
import pytest
import pytest_asyncio
import httpx
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.config import settings
from core.database import get_db
from main import app

from sqlalchemy import text
from core.database import Base
import models  # Ensure all models are registered

# Dedicated test engine with NullPool to prevent connection reuse issues
test_engine = create_async_engine(
    settings.DATABASE_URL,
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
    async with test_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(Base.metadata.create_all)
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

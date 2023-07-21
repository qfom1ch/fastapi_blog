import asyncio
from datetime import timedelta, datetime

import pytest

from starlette.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from app.user.security import create_access_token
from config import TEST_DATABASE_URL, ACCESS_TOKEN_EXPIRE_MINUTES
from typing import Generator, Any
import asyncpg
from db.session import get_db
from main import app
from db.session import Base

CLEAN_TABLES = [
    "posts",
    "users"
]


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def async_test_engine():
    async_test_engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=False,
                                            execution_options={"isolation_level": "AUTOCOMMIT"})
    yield async_test_engine


@pytest.fixture(scope="session", autouse=True)
async def async_session_test(async_test_engine):
    async_session = sessionmaker(bind=async_test_engine, expire_on_commit=False, class_=AsyncSession)
    yield async_session


@pytest.fixture(scope='session', autouse=True)
async def prepare_database(async_test_engine):
    async with async_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


from sqlalchemy.sql import text


@pytest.fixture(scope="function", autouse=True)
async def clean_tables(async_session_test):
    """Clean data in all tables before running test function"""
    async with async_session_test() as session:
        async with session.begin():
            for table_for_cleaning in CLEAN_TABLES:
                await session.execute(text(f"""DELETE FROM {table_for_cleaning};"""))


async def get_test_db() -> Generator:
    try:
        async_test_engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=False,
                                                execution_options={"isolation_level": "AUTOCOMMIT"})

        async_test_session = sessionmaker(bind=async_test_engine, expire_on_commit=False, class_=AsyncSession)
        session: AsyncSession = async_test_session()
        yield session
    finally:
        await session.close()


@pytest.fixture(scope="function")
async def client() -> Generator[TestClient, Any, None]:
    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
async def asyncpg_pool():
    pool = await asyncpg.create_pool(
        "".join(TEST_DATABASE_URL.split("+asyncpg"))
    )
    yield pool
    await pool.close()


@pytest.fixture
async def get_user_from_database(asyncpg_pool):
    async def get_user_from_database_by_id(user_id: str):
        async with asyncpg_pool.acquire() as connection:
            return await connection.fetch(
                """SELECT * FROM users WHERE id = $1;""", user_id
            )

    return get_user_from_database_by_id


@pytest.fixture
async def create_user_in_database(asyncpg_pool):
    async def create_user_in_database(
            id: int,
            username: str,
            email: str,
            is_active: bool,
            hashed_password: str,
            is_admin: bool,
            is_superuser: bool,

    ):
        async with asyncpg_pool.acquire() as connection:
            return await connection.execute(
                """INSERT INTO users VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                id,
                username,
                email,
                is_active,
                hashed_password,
                is_admin,
                is_superuser,
            )

    return create_user_in_database


@pytest.fixture
async def create_post_in_database(asyncpg_pool):
    async def create_post_in_database(
            id: int,
            author_id: int,
            slug: str,
            title: str,
            text: str,
            short_description: str,
            published_at: datetime,

    ):
        async with asyncpg_pool.acquire() as connection:
            return await connection.execute(
                """INSERT INTO posts VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                id,
                author_id,
                slug,
                title,
                text,
                short_description,
                published_at,
            )

    return create_post_in_database


def create_test_auth_headers_for_user(username: str) -> dict[str, str]:
    access_token = create_access_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"Authorization": f"Bearer {access_token}"}

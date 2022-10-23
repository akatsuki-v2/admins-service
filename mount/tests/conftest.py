from typing import AsyncIterator

import pytest
from app.common import settings
from app.common.context import Context
from app.services.database import dsn
from app.services.database import ServiceDatabase
from app.services.redis import ServiceRedis


# https://docs.pytest.org/en/7.1.x/reference/reference.html#globalvar-pytestmark
pytestmark = pytest.mark.asyncio


class TestContext(Context):
    def __init__(self, db: ServiceDatabase, redis: ServiceRedis) -> None:
        self._db = db
        self._redis = redis

    @property
    def db(self) -> ServiceDatabase:
        return self._db

    @property
    def redis(self) -> ServiceRedis:
        return self._redis


@pytest.fixture
async def db() -> AsyncIterator[ServiceDatabase]:
    async with ServiceDatabase(
        write_dsn=dsn(
            driver=settings.WRITE_DB_DRIVER,
            user=settings.WRITE_DB_USER,
            password=settings.WRITE_DB_PASS,
            host=settings.WRITE_DB_HOST,
            port=settings.WRITE_DB_PORT,
            database=settings.WRITE_DB_NAME,
        ),
        read_dsn=dsn(
            driver=settings.WRITE_DB_DRIVER,
            user=settings.READ_DB_USER,
            password=settings.READ_DB_PASS,
            host=settings.READ_DB_HOST,
            port=settings.READ_DB_PORT,
            database=settings.READ_DB_NAME,
        ),
        min_pool_size=settings.MIN_DB_POOL_SIZE,
        max_pool_size=settings.MAX_DB_POOL_SIZE,
        ssl=settings.DB_USE_SSL,
    ) as db:
        yield db


@pytest.fixture
async def redis() -> AsyncIterator[ServiceRedis]:
    async with ServiceRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
    ) as redis:
        yield redis


@pytest.fixture
async def ctx(db: ServiceDatabase, redis: ServiceRedis) -> TestContext:
    return TestContext(db=db, redis=redis)

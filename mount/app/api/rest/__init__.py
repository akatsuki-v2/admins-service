from __future__ import annotations

from app.api import middlewares
from app.common import settings
from app.services import database
from app.services import redis
from fastapi import FastAPI
from shared_modules import logger
from starlette.middleware.base import BaseHTTPMiddleware


def init_db(api: FastAPI) -> None:
    @api.on_event("startup")
    async def startup_db() -> None:
        logger.info("Starting up database pool")
        service_database = database.ServiceDatabase(
            read_dsn=database.dsn(
                driver=settings.WRITE_DB_DRIVER,
                user=settings.READ_DB_USER,
                password=settings.READ_DB_PASS,
                host=settings.READ_DB_HOST,
                port=settings.READ_DB_PORT,
                database=settings.READ_DB_NAME,
            ),
            write_dsn=database.dsn(
                driver=settings.WRITE_DB_DRIVER,
                user=settings.WRITE_DB_USER,
                password=settings.WRITE_DB_PASS,
                host=settings.WRITE_DB_HOST,
                port=settings.WRITE_DB_PORT,
                database=settings.WRITE_DB_NAME,
            ),
            min_pool_size=settings.MIN_DB_POOL_SIZE,
            max_pool_size=settings.MAX_DB_POOL_SIZE,
            ssl=settings.DB_USE_SSL,
        )
        await service_database.connect()
        api.state.db = service_database
        logger.info("Database pool started up")

    @api.on_event("shutdown")
    async def shutdown_db() -> None:
        logger.info("Shutting down database pool")
        await api.state.db.disconnect()
        del api.state.db
        logger.info("Database pool shut down")


def init_redis(api: FastAPI) -> None:
    @api.on_event("startup")
    async def startup_redis() -> None:
        logger.info("Starting up redis pool")
        service_redis = redis.ServiceRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
        )
        await service_redis.initialize()
        api.state.redis = service_redis
        logger.info("Redis pool started up")

    @api.on_event("shutdown")
    async def shutdown_redis() -> None:
        logger.info("Shutting down the redis")
        await api.state.redis.close()
        del api.state.redis
        logger.info("Redis pool shut down")


def init_middlewares(api: FastAPI) -> None:
    middleware_stack = [
        middlewares.add_process_time_header_to_response,
        middlewares.add_db_to_request,
        middlewares.add_redis_to_request,
    ]
    # NOTE: starlette reverses the order of the middleware stack
    # more info: https://github.com/encode/starlette/issues/479
    for middleware in reversed(middleware_stack):
        api.add_middleware(BaseHTTPMiddleware, dispatch=middleware)


def init_routes(api: FastAPI) -> None:
    from .v1 import router as v1_router

    api.include_router(v1_router)


def init_api():
    api = FastAPI()

    init_db(api)
    init_redis(api)
    init_middlewares(api)
    init_routes(api)

    return api

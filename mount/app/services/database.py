from __future__ import annotations

from types import TracebackType
from typing import Any
from typing import Mapping
from typing import Type

from aiomysql.cursors import DeserializationCursor
from databases import Database
from databases.core import Connection
from databases.core import Transaction


def _create_pool(dsn: str, min_pool_size: int, max_pool_size: int, ssl: bool) -> Database:
    return Database(url=dsn, min_size=min_pool_size, max_size=max_pool_size, ssl=ssl,
                    cursorclass=DeserializationCursor)


def dsn(
    driver: str,
    user: str,
    password: str,
    host: str,
    port: int,
    database: str,
) -> str:
    return f"{driver}://{user}:{password}@{host}:{port}/{database}"


class ServiceDatabase:
    def __init__(self, read_dsn: str, write_dsn: str,
                 min_pool_size: int, max_pool_size: int,
                 ssl: bool) -> None:
        self.read_pool = _create_pool(read_dsn,
                                      min_pool_size,
                                      max_pool_size,
                                      ssl)
        self.write_pool = _create_pool(write_dsn,
                                       min_pool_size,
                                       max_pool_size,
                                       ssl)

    async def __aenter__(self) -> ServiceDatabase:
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Type[BaseException] | None,
                        exc_value: None | BaseException | None,
                        traceback:  TracebackType | None) -> None:
        await self.disconnect()

    def connection(self) -> Connection:
        return self.read_pool.connection()

    def transaction(self) -> Transaction:
        return self.write_pool.transaction()

    async def connect(self) -> None:
        await self.read_pool.connect()
        await self.write_pool.connect()

    async def disconnect(self) -> None:
        await self.read_pool.disconnect()
        await self.write_pool.disconnect()

    async def fetch_one(self, query: str, values: dict | None = None) -> Mapping[str, Any] | None:
        async with self.read_pool.connection() as connection:
            return await connection.fetch_one(query, values)  # type: ignore

    async def fetch_all(self, query: str, values: dict | None = None) -> list[Mapping[str, Any]]:
        async with self.read_pool.connection() as connection:
            return await connection.fetch_all(query, values)  # type: ignore

    async def fetch_val(self, query: str, values: dict | None = None) -> Any:
        async with self.read_pool.connection() as connection:
            return await connection.fetch_val(query, values)  # type: ignore

    async def execute(self, query: str, values: dict | None = None) -> Any:
        async with self.write_pool.connection() as connection:
            return await connection.execute(query, values)  # type: ignore

    async def execute_many(self, query: str, values: list) -> None:
        async with self.write_pool.connection() as connection:
            return await connection.execute_many(query, values)

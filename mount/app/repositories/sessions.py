from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Literal
from typing import Mapping
from uuid import UUID

from app.common import json
from app.common.context import Context

SESSION_EXPIRY = 3600  # 1h


def create_session_key(session_id: UUID | Literal['*']) -> str:
    return f"users:sessions:{session_id}"

# TODO: is my usage of setex correct?
# i'm technically desyncing from the expires_at var


class SessionsRepo:
    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    async def create(self, session_id: UUID, account_id: int,
                     user_agent: str) -> Mapping[str, Any]:
        now = datetime.now()
        expires_at = now + timedelta(seconds=SESSION_EXPIRY)
        session = {
            "session_id": session_id,
            "account_id": account_id,
            "user_agent": user_agent,
            "expires_at": expires_at,
            "created_at": now,
            "updated_at": now,
        }
        await self.ctx.redis.setex(create_session_key(session_id),
                                   SESSION_EXPIRY, json.dumps(session))
        return session

    async def fetch_one(self, session_id: UUID) -> Mapping[str, Any] | None:
        session = await self.ctx.redis.get(create_session_key(session_id))
        if session is None:
            return None
        return json.loads(session)

    async def fetch_all(self, account_id: int | None = None,
                        user_agent: str | None = None,
                        page: int = 1, page_size: int = 10
                        ) -> list[Mapping[str, Any]]:
        session_key = create_session_key("*")

        if page > 1:
            cursor, keys = await self.ctx.redis.scan(cursor=0,
                                                     match=session_key,
                                                     count=(page - 1) * page_size)
        else:
            cursor = None

        sessions = []
        while cursor != 0:
            cursor, keys = await self.ctx.redis.scan(cursor=cursor or 0,
                                                     match=session_key,
                                                     count=page_size)

            raw_sessions = await self.ctx.redis.mget(keys)
            for raw_session in raw_sessions:
                session = json.loads(raw_session)

                if account_id is not None and session["account_id"] != account_id:
                    continue

                if user_agent is not None and session["user_agent"] != user_agent:
                    continue

                sessions.append(session)

        return sessions

    async def partial_update(self, session_id: UUID, **kwargs: Any) -> Mapping[str, Any] | None:
        raw_session = await self.ctx.redis.get(create_session_key(session_id))
        if raw_session is None:
            return None

        session = json.loads(raw_session)

        if not kwargs:
            return session

        session = dict(session)
        session.update(kwargs)
        session["updated_at"] = datetime.now()

        await self.ctx.redis.set(create_session_key(session_id), json.dumps(session))

        if expires_at := kwargs.get("expires_at"):
            await self.ctx.redis.expireat(create_session_key(session_id), expires_at)

        return session

    async def delete(self, session_id: UUID) -> Mapping[str, Any] | None:
        session_key = create_session_key(session_id)

        session = await self.ctx.redis.get(session_key)
        if session is None:
            return None

        await self.ctx.redis.delete(session_key)

        return json.loads(session)

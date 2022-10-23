from __future__ import annotations

from uuid import UUID

from app.api.rest.context import RequestContext
from app.common import responses
from app.common.errors import ServiceError
from app.common.responses import Success
from app.models.sessions import LoginForm
from app.models.sessions import Session
from app.models.sessions import SessionUpdate
from app.usecases import sessions
from fastapi import APIRouter
from fastapi import Depends

router = APIRouter()


# https://osuakatsuki.atlassian.net/browse/V2-11
@router.post("/v1/sessions", response_model=Success[Session])
async def log_in(args: LoginForm, ctx: RequestContext = Depends()):
    data = await sessions.log_in(ctx, identifier=args.identifier,
                                 passphrase=args.passphrase,
                                 user_agent=args.user_agent)
    if isinstance(data, ServiceError):
        return responses.failure(data, "Failed to create session")

    resp = Session.from_mapping(data)
    return responses.success(resp)


# https://osuakatsuki.atlassian.net/browse/V2-13
@router.delete("/v1/sessions/{session_id}", response_model=Success[Session])
async def log_out(session_id: UUID, ctx: RequestContext = Depends()):
    data = await sessions.log_out(ctx, session_id)
    if isinstance(data, ServiceError):
        return responses.failure(data, "Failed to delete session")

    resp = Session.from_mapping(data)
    return responses.success(resp)


@router.get("/v1/sessions/{session_id}", response_model=Success[Session])
async def fetch_one(session_id: UUID, ctx: RequestContext = Depends()):
    data = await sessions.fetch_one(ctx, session_id)
    if isinstance(data, ServiceError):
        return responses.failure(data, "Failed to fetch session")

    resp = Session.from_mapping(data)
    return responses.success(resp)


@router.get("/v1/sessions", response_model=Success[Session])
async def fetch_all(account_id: int | None = None,
                    user_agent: str | None = None,
                    ctx: RequestContext = Depends()):
    data = await sessions.fetch_all(ctx, account_id=account_id,
                                    user_agent=user_agent)
    if isinstance(data, ServiceError):
        return responses.failure(data, "Failed to fetch sessions")

    return responses.success(data)


# https://osuakatsuki.atlassian.net/browse/V2-12
@router.patch("/v1/sessions/{session_id}", response_model=Success[Session])
async def partial_update_session(session_id: UUID, args: SessionUpdate,
                                 ctx: RequestContext = Depends()):
    data = await sessions.partial_update(ctx, session_id,
                                         expires_at=args.expires_at)
    if isinstance(data, ServiceError):
        return responses.failure(data, "Failed to update session")

    resp = Session.from_mapping(data)
    return responses.success(resp)

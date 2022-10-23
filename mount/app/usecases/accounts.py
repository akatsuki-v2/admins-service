from __future__ import annotations

import traceback
from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from app.common import security
from app.common import validation
from app.common.context import Context
from app.common.errors import ServiceError
from app.models import Status
from app.repositories.accounts import AccountsRepo
from app.repositories.credentials import CredentialsRepo
from shared_modules import logger


async def sign_up(ctx: Context,
                  username: str,
                  password: str,
                  email_address: str) -> Mapping[str, Any] | ServiceError:
    a_repo = AccountsRepo(ctx)
    c_repo = CredentialsRepo(ctx)

    # perform data validation

    if not validation.validate_username(username):
        return ServiceError.ACCOUNTS_USERNAME_INVALID

    if not validation.validate_password(password):
        return ServiceError.ACCOUNTS_PASSWORD_INVALID

    if not validation.validate_email(email_address):
        return ServiceError.ACCOUNTS_EMAIL_ADDRESS_INVALID

    if await a_repo.fetch_one(email_address=email_address) is not None:
        return ServiceError.ACCOUNTS_EMAIL_ADDRESS_EXISTS

    if await a_repo.fetch_one(username=username) is not None:
        return ServiceError.ACCOUNTS_USERNAME_EXISTS

    transaction = await ctx.db.transaction()

    try:
        account = await a_repo.create(username=username,
                                      email_address=email_address)
        account_id = account["account_id"]

        hashed_password = await security.hash_password(password)

        # create two sets of credentials for the user;
        # allow them to login in via username or email address
        for identifier_type, identifier, passphrase in (
            ("username", username, hashed_password),
            ("email", email_address, hashed_password),
        ):
            credentials_id = uuid4()
            await c_repo.create(credentials_id=credentials_id,
                                account_id=account_id,
                                identifier_type=identifier_type,
                                identifier=identifier,
                                passphrase=passphrase)

    except Exception as exc:  # pragma: no cover
        await transaction.rollback()
        logger.error("Unable to create account:", error=exc)
        logger.error("Stack trace: ", error=traceback.format_exc())
        return ServiceError.ACCOUNTS_CANNOT_CREATE
    else:
        await transaction.commit()

    return account


async def fetch_one(ctx: Context,
                    account_id: int | None = None,
                    username: str | None = None,
                    email_address: str | None = None,
                    country: str | None = None,
                    status: Status | None = Status.ACTIVE) -> Mapping[str, Any] | ServiceError:
    repo = AccountsRepo(ctx)

    account = await repo.fetch_one(account_id=account_id,
                                   username=username,
                                   email_address=email_address,
                                   status=status)
    if account is None:
        return ServiceError.ACCOUNTS_NOT_FOUND

    return account


async def fetch_all(ctx: Context, country: str | None = None,
                    status: Status | None = Status.ACTIVE) -> list[Mapping[str, Any]]:
    repo = AccountsRepo(ctx)
    accounts = await repo.fetch_all(status=status)
    return accounts


async def partial_update(ctx: Context,
                         account_id: int,
                         **kwargs: Any | None) -> Mapping[str, Any] | ServiceError:
    repo = AccountsRepo(ctx)

    account = await repo.fetch_one(account_id)
    if account is None:
        return ServiceError.ACCOUNTS_NOT_FOUND

    updates = {}

    new_username = kwargs.get("username")
    if new_username is not None and new_username != account["username"]:
        if not validation.validate_username(new_username):
            return ServiceError.ACCOUNTS_USERNAME_INVALID

        if await repo.fetch_one(username=new_username) is not None:
            return ServiceError.ACCOUNTS_USERNAME_EXISTS

        updates["username"] = new_username

    new_email_address = kwargs.get("email_address")
    if new_email_address is not None and new_email_address != account["email_address"]:
        if not validation.validate_email(new_email_address):
            return ServiceError.ACCOUNTS_EMAIL_ADDRESS_INVALID

        if await repo.fetch_one(email_address=new_email_address) is not None:
            return ServiceError.ACCOUNTS_EMAIL_ADDRESS_EXISTS

        updates["email_address"] = new_email_address
        updates["email_address_verification_time"] = None

    new_status = kwargs.get("status")
    if new_status is not None and new_status != account["status"]:
        updates["status"] = new_status

    if not updates:
        # return the account as-is
        return account

    account = await repo.partial_update(account_id, **updates)
    assert account is not None
    return account


async def delete(ctx: Context, account_id: int) -> Mapping[str, Any] | ServiceError:
    a_repo = AccountsRepo(ctx)
    c_repo = CredentialsRepo(ctx)

    transaction = await ctx.db.transaction()

    try:
        account = await a_repo.delete(account_id)
        if account is None:
            return ServiceError.ACCOUNTS_NOT_FOUND

        all_active_credentials = await c_repo.fetch_all(account_id=account_id,
                                                        status=Status.ACTIVE)
        for active_credentials in all_active_credentials:
            credentials = await c_repo.delete(active_credentials["credentials_id"])
            assert credentials is not None

    except Exception as exc:  # pragma: no cover
        await transaction.rollback()
        logger.error("Unable to delete account:", error=exc)
        logger.error("Stack trace: ", error=traceback.format_exc())
        return ServiceError.ACCOUNTS_CANNOT_DELETE
    else:
        await transaction.commit()

    return account

from __future__ import annotations

from datetime import datetime

from . import BaseModel
from . import Status


class SignupForm(BaseModel):
    username: str
    password: str
    email_address: str


class Account(BaseModel):
    account_id: int
    username: str
    email_address: str

    status: Status
    created_at: datetime
    updated_at: datetime


class AccountUpdate(BaseModel):
    username: str | None
    email_address: str | None

    # private endpoint feature
    # not to be exposed to users
    status: Status | None

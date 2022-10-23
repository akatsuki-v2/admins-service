from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from typing import Mapping
from uuid import UUID

from . import BaseModel
from . import Status


class IdentifierType(str, Enum):
    EMAIL = "email"
    USERNAME = "username"

    # TODO: biometrics?
    # TODO: phone?


class Credentials(BaseModel):
    rec_id: int
    credentials_id: UUID
    account_id: int
    identifier_type: IdentifierType
    identifier: str
    passphrase: str

    status: Status
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> Credentials:
        return cls(
            rec_id=mapping["rec_id"],
            credentials_id=mapping["credentials_id"],
            account_id=mapping["account_id"],
            identifier_type=mapping["identifier_type"],
            identifier=mapping["identifier"],
            passphrase=mapping["passphrase"],
            status=mapping["status"],
            created_at=mapping["created_at"],
            updated_at=mapping["updated_at"],
        )


class CredentialsUpdate(BaseModel):
    passphrase: str | None

    # private endpoint feature
    # not to be exposed to users
    status: Status

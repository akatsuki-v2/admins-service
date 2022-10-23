from __future__ import annotations

from enum import Enum


class ServiceError(str, Enum):
    ACCOUNTS_CANNOT_CREATE = 'accounts.cannot_create'
    ACCOUNTS_CANNOT_DELETE = 'accounts.cannot_delete'
    ACCOUNTS_NOT_FOUND = 'accounts.not_found'
    ACCOUNTS_USERNAME_INVALID = 'accounts.username_invalid'
    ACCOUNTS_PASSWORD_INVALID = 'accounts.password_invalid'
    ACCOUNTS_EMAIL_ADDRESS_INVALID = 'accounts.email_address_invalid'
    ACCOUNTS_COUNTRY_INVALID = 'accounts.country_invalid'
    ACCOUNTS_EMAIL_ADDRESS_EXISTS = 'accounts.email_address_exists'
    ACCOUNTS_USERNAME_EXISTS = 'accounts.username_exists'

    CREDENTIALS_CANNOT_CREATE = 'credentials.cannot_create'
    CREDENTIALS_CANNOT_DELETE = 'credentials.cannot_delete'
    CREDENTIALS_NOT_FOUND = 'credentials.incorrect_credentials'
    CREDENTIALS_INCORRECT = 'credentials.incorrect_credentials'

    SESSIONS_CANNOT_CREATE = 'sessions.cannot_create'
    SESSIONS_CANNOT_DELETE = 'sessions.cannot_delete'
    SESSIONS_NOT_FOUND = 'sessions.not_found'

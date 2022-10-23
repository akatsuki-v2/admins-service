import pytest
from app.common.context import Context
from app.common.errors import ServiceError
from app.usecases import accounts

# https://docs.pytest.org/en/7.1.x/reference/reference.html#globalvar-pytestmark
pytestmark = pytest.mark.asyncio


async def test_should_pass(ctx: Context):
    assert ctx is not None


async def test_should_signup(ctx: Context):
    username = "cmyui"
    password = "aBcDe#4rFg"
    email_address = "cmyuiosu@gmail.com"
    data = await accounts.sign_up(ctx,
                                  username=username,
                                  password=password,
                                  email_address=email_address)
    assert not isinstance(data, ServiceError)

    assert data["account_id"] is not None
    assert data["username"] == username
    assert data["email_address"] == email_address
    assert data["created_at"] is not None
    assert data["updated_at"] is not None

    # TODO: should we check the credentials were created correctly?


async def test_should_fail_signup_invalid_email(ctx: Context):
    username = "invalid_email"
    password = "aBcDe#4rFg"
    email_address = "invalid_email"
    data = await accounts.sign_up(ctx,
                                  username=username,
                                  password=password,
                                  email_address=email_address)
    assert isinstance(data, ServiceError)
    assert data == ServiceError.ACCOUNTS_EMAIL_ADDRESS_INVALID


async def test_should_fail_signup_duplicate_email(ctx: Context):
    username = "duplicate_email"
    password = "aBcDe#4rFg"
    email_address = "duplicate_email@gmail.com"
    data = await accounts.sign_up(ctx,
                                  username=username,
                                  password=password,
                                  email_address=email_address)
    assert not isinstance(data, ServiceError)

    data = await accounts.sign_up(ctx,
                                  username=username,
                                  password=password,
                                  email_address=email_address)
    assert isinstance(data, ServiceError)
    assert data == ServiceError.ACCOUNTS_EMAIL_ADDRESS_EXISTS


async def test_should_fail_signup_duplicate_username(ctx: Context):
    username = "duplicate_name"
    password = "aBcDe#4rFg"
    email_address = "duplicate_name@gmail.com"
    data = await accounts.sign_up(ctx,
                                  username=username,
                                  password=password,
                                  email_address=email_address)
    assert not isinstance(data, ServiceError)

    email_address = "duplicate_name2@gmail.com"
    data = await accounts.sign_up(ctx,
                                  username=username,
                                  password=password,
                                  email_address=email_address)
    assert isinstance(data, ServiceError)
    assert data == ServiceError.ACCOUNTS_USERNAME_EXISTS


async def test_should_fetch_one(ctx: Context):
    username = "fetch_one"
    password = "aBcDe#4rFg"
    email_address = "fetch_one@gmail.com"
    data = await accounts.sign_up(ctx,
                                  username=username,
                                  password=password,
                                  email_address=email_address)
    assert not isinstance(data, ServiceError)

    account_id = data["account_id"]
    data = await accounts.fetch_one(ctx, account_id=account_id)
    assert not isinstance(data, ServiceError)

    assert data["account_id"] == account_id
    assert data["username"] == username
    assert data["email_address"] == email_address
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


async def test_should_fail_fetch_one_no_account(ctx: Context):
    account_id = 1234
    data = await accounts.fetch_one(ctx, account_id=account_id)
    assert isinstance(data, ServiceError)
    assert data == ServiceError.ACCOUNTS_NOT_FOUND


async def test_should_fetch_all(ctx: Context):
    data = await accounts.fetch_all(ctx)
    assert not isinstance(data, ServiceError)


async def test_should_partial_update(ctx: Context):
    username = "partial_update"
    password = "aBcDe#4rFg"
    email_address = "partial_update@gmail.com"
    data = await accounts.sign_up(ctx,
                                  username=username,
                                  password=password,
                                  email_address=email_address)
    assert not isinstance(data, ServiceError)

    account_id = data["account_id"]
    new_username = "partial_update2"
    data = await accounts.partial_update(ctx,
                                         account_id=account_id,
                                         username=new_username)
    assert not isinstance(data, ServiceError)

    assert data["account_id"] == account_id
    assert data["username"] == new_username
    assert data["email_address"] == email_address
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


async def test_should_fail_partial_update_no_account(ctx: Context):
    account_id = 1234
    new_username = "partial_update2"
    data = await accounts.partial_update(ctx,
                                         account_id=account_id,
                                         username=new_username)
    assert isinstance(data, ServiceError)
    assert data == ServiceError.ACCOUNTS_NOT_FOUND


async def test_should_fail_partial_update_no_changes(ctx: Context):
    username = "partial_update3"
    password = "aBcDe#4rFg"
    email_address = "partial_update_no_changes@gmail.com"
    data = await accounts.sign_up(ctx,
                                  username=username,
                                  password=password,
                                  email_address=email_address)
    assert not isinstance(data, ServiceError)

    account_id = data["account_id"]
    data = await accounts.partial_update(ctx,
                                         account_id=account_id)
    assert not isinstance(data, ServiceError)

    assert data["account_id"] == account_id
    assert data["username"] == username
    assert data["email_address"] == email_address
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


async def test_should_delete(ctx: Context):
    username = "delete"
    password = "aBcDe#4rFg"
    email_address = "delete@gmail.com"
    data = await accounts.sign_up(ctx,
                                  username=username,
                                  password=password,
                                  email_address=email_address)
    assert not isinstance(data, ServiceError)

    account_id = data["account_id"]
    data = await accounts.delete(ctx, account_id=account_id)
    assert not isinstance(data, ServiceError)

    data = await accounts.fetch_one(ctx, account_id=account_id)
    assert isinstance(data, ServiceError)
    assert data == ServiceError.ACCOUNTS_NOT_FOUND


async def test_should_fail_delete_no_account(ctx: Context):
    account_id = 1234
    data = await accounts.delete(ctx, account_id=account_id)
    assert isinstance(data, ServiceError)
    assert data == ServiceError.ACCOUNTS_NOT_FOUND

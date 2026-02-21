import datetime
import hashlib
import os
import random

import argon2
import grammdb
import grammlog
import jwt

from pykc.common import (
    logs,
    timestamps,
)
from pykc.dl import (
    crud,
    db,
)
from pykc.exceptions import DataError
from pykc.sl import errors
from pykc.sl.errors import Err
from pykc.types import PK


def generate_token(lifetime: int, **additional_data) -> str:
    now = timestamps.now()
    token_lifetime = datetime.timedelta(minutes=lifetime)
    payload = {
        "r": str(random.randbytes(4)),
        "exp": now + token_lifetime,
        "iat": now,
        **additional_data,
    }
    token = jwt.encode(payload, os.environ["JWT_SECRET"], algorithm="HS256")
    return token


def hash_token(jwt: str) -> str:
    return hashlib.sha1(jwt.encode()).hexdigest()


def generate_csrf() -> str:
    """Generate a csrf token for a page render."""

    return generate_token(1440)


def is_token_valid(token: str) -> bool:
    """Validate a JWT and return a bool indicating if it is valid or not."""

    try:
        validate_token(token)
        return True
    except jwt.InvalidTokenError:
        return False


def validate_token(token: str) -> dict:
    """Validate a JWT token and return the stored payload."""

    return jwt.decode(token, os.environ["JWT_SECRET"], algorithms=["HS256"])


def generate_bearer(member_id: PK) -> str:
    """Generate a bearer token for the logged in user."""

    return generate_token(5, member_id=member_id)


async def verify_api_key(api_token: str) -> tuple[Err, str]:
    """Verify an issued api key.

    Returns:
        A `pykc.sl.errors.ErrorTuple` containing the verified token_id if successful.
    """

    tr = await grammdb.start_transaction(db.members())
    try:
        token_record = (await errors.raise_if_err(crud.get_token_by_hash(tr, api_token)))._tuple()
    except DataError:
        return Err.AUTH, "invalid api token"
    finally:
        await grammdb.close_transaction(tr)
    if is_token_valid(token_record.jwt):
        return Err.OK, token_record.hash
    else:
        return Err.AUTH, "invalid api token"


_ARGON: argon2.PasswordHasher | None = None


def pw_hasher() -> argon2.PasswordHasher:
    """Return a constant PasswordHasher instance with particular argon2id parameters.

    This is returned as a constant in order to avoid the additional timing channel that
    creating the instance on each use would incur.

    We use three iterations, one thread, and 12 MB of memory per OWASP recommendations:
      https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#argon2id

    See also:
      https://argon2-cffi.readthedocs.io/en/stable/api.html
    """

    global _ARGON
    if _ARGON is None:
        _ARGON = argon2.PasswordHasher(time_cost=3, memory_cost=12288, parallelism=1)
    return _ARGON


async def verify_member_password(moniker: str, pw: str) -> tuple[Err, str | PK]:
    """Verify a member's password login.

    Returns:
        A `pykc.sl.errors.ErrorTuple` containing the verified member_id if successful.
    """

    tr = await grammdb.start_transaction(db.members())

    try:
        # We need to use the dl functions directly since the MemberStruct strips the password hash.
        member = (await errors.raise_if_err(crud.get_member_by_moniker(tr, moniker)))._tuple()
    except DataError:
        return Err.INVALID, "invalid moniker"
    finally:
        await grammdb.close_transaction(tr)

    try:
        pw_hasher().verify(member.password_hash, pw)
        return Err.OK, member.id
    except argon2.exceptions.VerifyMismatchError as e:
        await grammlog.async_debug(
            logs.err_log,
            "Incorrect password provided in request",
            {"domain": "auth", "caller": verify_member_password.__qualname__, "moniker": moniker},
            err=e,
        )
        return Err.INVALID, "password is incorrect"
    except argon2.exceptions.VerificationError as e:
        await grammlog.async_debug(
            logs.err_log,
            "Invalid password hash read from database",
            {"domain": "auth", "caller": verify_member_password.__qualname__, "moniker": moniker},
            err=e,
        )
        return Err.INVALID, "password is incorrect"

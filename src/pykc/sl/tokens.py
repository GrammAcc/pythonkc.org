import datetime
import hashlib
import os
import random

import grammdb
import jwt

from pykc.common import timestamps
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

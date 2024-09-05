import datetime
from collections.abc import Sequence

import jwt

import config


def encode_jwt(payload: dict, expires: datetime.timedelta | int) -> str:
    if isinstance(expires, int):
        expires = datetime.timedelta(seconds=expires)
    payload = payload.copy()
    payload.setdefault('exp', datetime.datetime.now() + expires)
    return jwt.encode(payload, config.SECRET_KEY, config.JWT_ENCODE_ALGORITHM)


def decode_jwt(token: str, required_keys: Sequence[str] = None) -> dict | None:
    required_keys = required_keys or []
    if token is None:
        return
    try:
        payload = jwt.decode(token, config.SECRET_KEY, config.DECODE_JWT_ALGORITHMS)
        for key in required_keys:
            if key not in payload:
                return
        return payload
    except jwt.InvalidTokenError:
        return None

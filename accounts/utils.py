import asyncio
import hashlib
import base64
import random
import secrets
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from accounts.db import get_user_by_email, user_with_email_exists
from db.models import User
from utils import encode_jwt
from mail import send_email


async def hash_password(
        raw_password: str,
        salt: str = None,
        algorithm: str = 'SHA256',
        iterations: int = 720_000
):
    salt = salt or secrets.token_urlsafe(random.randint(15, 25))
    hash = await asyncio.to_thread(  # pbkdf2_hmac releases GIL
        hashlib.pbkdf2_hmac,
        algorithm,
        raw_password.encode('utf-8'),
        salt.encode('utf-8'),
        iterations,
        None
    )
    hash = base64.b64encode(hash).decode('ascii').strip()
    return f'{hash}${salt}${algorithm}${iterations}'


async def check_password(password_hash: str, raw_password: str) -> bool:
    _, salt, algorithm, iterations = password_hash.split('$')
    return password_hash == await hash_password(raw_password, salt, algorithm, int(iterations))


async def authenticate(session: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(session, email)
    if user is None:
        return
    if await check_password(user.password_hash, password):
        return user


async def pre_send_confirm_email_check(db_session: AsyncSession, confirm_email_url: str, email):
    if '$TOKEN$' not in confirm_email_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='confirm_email_url must contain $TOKEN$')
    if await user_with_email_exists(db_session, email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User with such email already exists')


def send_confirm_email(confirm_email_url: str, user_uuid: UUID, email: str):
    token = encode_jwt({'user_uuid': user_uuid.hex, 'email': email}, 60 * 60 * 2)
    url = confirm_email_url.replace('$TOKEN$', token)
    send_email.delay(email, f'someone asked for confirming email in internetshop. If it weren\'t'
                            f'you, ignore this message. To confirm, follow this link: {url}')

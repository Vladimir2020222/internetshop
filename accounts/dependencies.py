from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from accounts import get_user_by_uuid
from db import get_async_session
from db.models import User
from utils import decode_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/accounts/login')


def get_current_user_uuid(token: Annotated[str, Depends(oauth2_scheme)]) -> UUID | None:
    payload = decode_jwt(token, ['user_uuid'])
    if payload is None:
        return
    return UUID(payload['user_uuid'])


def get_current_user_uuid_or_401(uuid: Annotated[UUID, Depends(get_current_user_uuid)]) -> UUID:
    if uuid is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    return uuid


async def get_current_user(
        uuid: Annotated[UUID, Depends(get_current_user_uuid)],
        db_session: Annotated[AsyncSession, Depends(get_async_session)]
) -> User | None:
    if uuid is None:
        return
    return await get_user_by_uuid(db_session, uuid)


async def get_current_user_or_401(
        current_user: Annotated[User | None, Depends(get_current_user)]
) -> User:
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    return current_user

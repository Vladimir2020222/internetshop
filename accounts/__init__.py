import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Form, Query, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from accounts.db import get_user_by_uuid, user_with_email_exists, create_user, update_user_email, update_user_full_name
from accounts.dependencies import get_current_user_or_401, get_current_user_uuid_or_401
from accounts.models import UserDTO
from accounts.utils import authenticate, hash_password, send_confirm_email, pre_send_confirm_email_check
from db import get_async_session
from db.models import User
from utils import encode_jwt, decode_jwt

router = APIRouter(prefix='/accounts')


@router.post('/login')
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db_session: Annotated[AsyncSession, Depends(get_async_session)]
):
    user = await authenticate(db_session, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect username or password')
    token = encode_jwt({'user_uuid': user.uuid.hex}, datetime.timedelta(days=60))
    return {'token_type': 'bearer', 'access_token': token}


@router.post('/signup')
async def signup(
        full_name: Annotated[str, Form()],
        email: Annotated[str, Form()],
        password: Annotated[str, Form()],
        confirm_email_url: Annotated[str, Query()],
        db_session: Annotated[AsyncSession, Depends(get_async_session)]
):
    await pre_send_confirm_email_check(db_session, confirm_email_url, email)
    password_hash = await hash_password(password)
    user_uuid = await create_user(db_session, full_name, password_hash)
    send_confirm_email(confirm_email_url, user_uuid, email)


@router.post('/confirm_email')
async def confirm_email(
        token: Annotated[str, Body(embed=True)],
        db_session: Annotated[AsyncSession, Depends(get_async_session)]
):
    payload = decode_jwt(token, ['user_uuid', 'email'])
    if payload is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid token')
    email = payload['email']
    user_uuid = UUID(payload['user_uuid'])
    await update_user_email(db_session, user_uuid, email)


@router.get('/profile', response_model=UserDTO)
async def get_profile(user: Annotated[User, Depends(get_current_user_or_401)]):
    return user


@router.patch('/profile/update')
async def update_profile(
        user_uuid: Annotated[UUID, Depends(get_current_user_uuid_or_401)],
        db_session: Annotated[AsyncSession, Depends(get_async_session)],
        confirm_email_url: Annotated[str | None, Query()] = None,
        full_name: Annotated[str | None, Body()] = None,
        email: Annotated[str | None, Body()] = None
):
    if email:
        if confirm_email_url is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='email is provided, but confirm_email_url is not'
            )
        await pre_send_confirm_email_check(db_session, confirm_email_url, email)
        send_confirm_email(confirm_email_url, user_uuid, email)
    if full_name:
        await update_user_full_name(db_session, user_uuid, full_name)

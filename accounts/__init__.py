import datetime
import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Form, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from accounts.db import get_user_by_uuid, user_with_email_exists, create_user
from accounts.utils import authenticate, hash_password
from db import get_async_session
from mail import send_email
from utils import encode_jwt

router = APIRouter(prefix='/accounts')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/accounts/login')


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


async def signup(
        full_name: Annotated[str, Form()],
        email: Annotated[str, Form()],
        password: Annotated[str, Form()],
        confirm_email_url: Annotated[str, Query()],
        db_session: Annotated[AsyncSession, Depends(get_async_session)]
):
    if await user_with_email_exists(db_session, email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User with such email already exists')
    password_hash = await hash_password(password)
    user_uuid = await create_user(db_session, full_name, password_hash)
    token = encode_jwt({'user_uuid': user_uuid.hex, 'email': email}, 60 * 60 * 2)
    url = confirm_email_url.replace('$TOKEN$', token)
    send_email.delay(email, f'someone asked for confirming email in internetshop. If it weren\'t'
                            f'you, ignore this message. To confirm, follow this link: {url}')

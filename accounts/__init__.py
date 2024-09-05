import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from accounts.db import get_user_by_uuid
from accounts.utils import authenticate
from db import get_async_session
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
    token = encode_jwt({'user_uuid': user.uuid.hex}, datetime.timedelta(days=))
    return {'token_type': 'bearer', 'access_token': token}

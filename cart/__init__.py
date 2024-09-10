from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

import cart.db
from accounts import get_current_user_uuid_or_401
from cart.db import get_user_products
from db import get_async_session
from db.models import Product

router = APIRouter(prefix='/cart')


@router.get('/')
async def get_all_products(
        user_uuid: Annotated[UUID, Depends(get_current_user_uuid_or_401)],
        db_session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await get_user_products(db_session, user_uuid)


@router.post('/add_product')
async def add_product_to_cart(
        user_uuid: Annotated[UUID, Depends(get_current_user_uuid_or_401)],
        product_uuid: Annotated[UUID, Body()],
        amount: Annotated[int, Body()],
        db_session: Annotated[AsyncSession, Depends(get_async_session)]
):
    await cart.db.add_product_to_cart(db_session, product_uuid, user_uuid, amount)


@router.post('/remove_product')
async def remove_product_from_cart(
        user_uuid: Annotated[UUID, Depends(get_current_user_uuid_or_401)],
        product_uuid: Annotated[UUID, Body(embed=True)],
        db_session: Annotated[AsyncSession, Depends(get_async_session)]
):
    await cart.db.remove_product_from_cart(db_session, product_uuid, user_uuid)

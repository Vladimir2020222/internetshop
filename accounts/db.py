from uuid import UUID

from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, Cart


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    res = await session.execute(select(User).where(User.email == email))
    return res.scalar()


async def user_with_email_exists(session: AsyncSession, email: str) -> bool:
    res = await session.execute(select(1).where(User.email == email))
    return bool(res.scalar())


async def get_user_by_uuid(session: AsyncSession, uuid: UUID) -> User | None:
    return await session.get(User, uuid)


async def create_user(session: AsyncSession, full_name: str, password_hash: str) -> UUID:
    cart_cte = insert(Cart).returning(Cart.uuid).cte()
    res = await session.execute(insert(User).values({
        'full_name': full_name,
        'password_hash': password_hash,
        'cart_uuid': select(cart_cte.c.uuid).scalar_subquery()
    }).returning(User.uuid))
    await session.commit()
    return res.scalar()


async def update_user_email(session: AsyncSession, user_uuid: UUID, email: str) -> None:
    await session.execute(update(User).where(User.uuid == user_uuid).values({'email': email}))
    await session.commit()


async def update_user_full_name(session: AsyncSession, user_uuid: UUID, full_name: str) -> None:
    await session.execute(update(User).where(User.uuid == user_uuid).values({'full_name': full_name}))
    await session.commit()


async def update_user_password(session: AsyncSession, user_uuid: UUID, password_hash: str) -> None:
    await session.execute(update(User).where(User.uuid == user_uuid).values({'password_hash': password_hash}))
    await session.commit()


async def update_user_password_by_email(session: AsyncSession, email: str, password_hash: str) -> None:
    await session.execute(update(User).where(User.email == email).values({'password_hash': password_hash}))
    await session.commit()

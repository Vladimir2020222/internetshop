from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    res = await session.execute(select(User).where(User.email == email))
    return res.scalar()


async def get_user_by_uuid(session: AsyncSession, uuid: UUID) -> User | None:
    return await session.get(User, uuid)

from uuid import UUID

from sqlalchemy import select, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import product_user_association_table, Product


async def get_user_products(session: AsyncSession, user_uuid: UUID) -> list[tuple[Product, int]]:
    statement = select(Product, product_user_association_table.c.amount) \
        .join(product_user_association_table) \
        .where(product_user_association_table.c.user_uuid == user_uuid)
    res = await session.execute(statement)
    return [(row[0], row[1]) for row in res.fetchall()]


async def add_product_to_cart(session: AsyncSession, product_uuid: UUID, user_uuid: UUID, amount: int) -> None:
    await session.execute(insert(product_user_association_table).values({
        'product_uuid': product_uuid,
        'user_uuid': user_uuid,
        'amount': amount
    }))
    await session.commit()


async def remove_product_from_cart(session: AsyncSession, product_uuid: UUID, user_uuid: UUID) -> None:
    await session.execute(delete(product_user_association_table).where(
        product_user_association_table.c.product_uuid == product_uuid,
        product_user_association_table.c.user_uuid == user_uuid
    ))
    await session.commit()


async def change_amount(session: AsyncSession, product_uuid: UUID, user_uuid: UUID, new_amount: int) -> None:
    statement = update(product_user_association_table) \
        .where(product_user_association_table.c.product_uuid == product_uuid,
               product_user_association_table.c.user_uuid == user_uuid) \
        .values({'amount': new_amount})
    await session.execute(statement)
    await session.commit()

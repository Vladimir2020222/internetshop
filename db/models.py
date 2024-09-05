import enum
from uuid import UUID

import sqlalchemy
from sqlalchemy import text, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserRole(enum.Enum):
    customer = 'customer'
    support = 'support'
    warehouse_worker = 'warehouse_worker'
    courier = 'courier'
    manager = 'manager'


class User(Base):
    __tablename__ = 'users'

    uuid: Mapped[UUID] = mapped_column(primary_key=True, server_default=text('gen_random_uuid()'))
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(320), unique=True)  # 320 is standardised max email length
    password_hash: Mapped[str]
    cart_uuid: Mapped[UUID] = mapped_column(
        ForeignKey('carts.uuid', name='users_cart_uuid_fkey', ondelete='RESTRICT'), unique=True
    )
    role: Mapped[UserRole] = mapped_column(sqlalchemy.Enum(UserRole), server_default=text("'customer'"))


class Cart(Base):
    __tablename__ = 'carts'

    uuid: Mapped[UUID] = mapped_column(primary_key=True, server_default=text('gen_random_uuid()'))

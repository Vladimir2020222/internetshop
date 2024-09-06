import enum
from uuid import UUID

import sqlalchemy
from sqlalchemy import text, String, ForeignKey, Integer, JSON, Table, Column, UniqueConstraint
from sqlalchemy.dialects.postgresql import TSVECTOR
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


product_cart_association_table = Table(
    'product_cart',
    Base.metadata,
    Column('product_uuid', ForeignKey(
        'products.uuid', ondelete='CASCADE', name='product_cart_product_uuid_fkey'
    ), primary_key=True),
    Column('cart_uuid', ForeignKey(
        'carts.uuid', ondelete='CASCADE', name='product_cart_cart_product_uuid_fkey'
    ), primary_key=True),
    Column('amount', Integer, nullable=False)
)


user_favorite_products = Table(
    'user_favorite_products',
    Base.metadata,
    Column('user_uuid', ForeignKey(
        'users.uuid', ondelete='CASCADE', name='user_favorite_products_user_uuid_fkey'
    ), primary_key=True),
    Column('product_uuid', ForeignKey(
        'products.uuid', ondelete='CASCADE', name='user_favorite_products_product_uuid_fkey'
    ), primary_key=True)
)


class ProductType(Base):
    __tablename__ = 'product_types'

    uuid: Mapped[UUID] = mapped_column(primary_key=True, server_default=text('gen_random_uuid()'))
    parent_uuid: Mapped[UUID | None] = mapped_column(
        ForeignKey('product_types.uuid', name='product_type_product_type_uuid_fkey', ondelete='CASCADE')
    )
    title: Mapped[str] = mapped_column(String(length=80))


class Product(Base):
    __tablename__ = 'products'

    uuid: Mapped[UUID] = mapped_column(primary_key=True, server_default=text('gen_random_uuid()'))
    price: Mapped[int] = mapped_column(
        Integer, sqlalchemy.CheckConstraint('price > 0'), name='price_positive'
    )
    title: Mapped[str] = mapped_column(String(length=300))
    description: Mapped[str] = mapped_column(String(length=5000))
    characteristics: Mapped[dict | None] = mapped_column(JSON)
    discount: Mapped[int] = mapped_column(
        Integer, sqlalchemy.CheckConstraint('discount <= 100 AND discount >= 0', name='check_discount'),
        server_default=text('0')
    )
    type_uuid: Mapped[UUID] = mapped_column(
        ForeignKey('product_types.uuid', name='products_product_types_uuid_fkey', ondelete='RESTRICT')
    )
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR)


class Review(Base):
    __tablename__ = 'reviews'
    # this unique constraint prevents user to have more than one review on the same product
    __table_args__ = (UniqueConstraint('product_uuid', 'author_uuid', name='product_author_unique'),)
    max_text_length = 1000

    uuid: Mapped[UUID] = mapped_column(primary_key=True, server_default=text('gen_random_uuid()'))
    product_uuid: Mapped[UUID] = mapped_column(
        ForeignKey('products.uuid', ondelete='CASCADE', name='reviews_product_uuid_fkey')
    )
    author_uuid: Mapped[UUID] = mapped_column(
        ForeignKey('users.uuid', ondelete='CASCADE', name='reviews_author_uuid_fkey')
    )
    text: Mapped[str] = mapped_column(String(length=max_text_length))
    rate: Mapped[int] = mapped_column(
        Integer, sqlalchemy.CheckConstraint('rate <= 5 AND rate >= 1', name='check_rate')
    )


class ReviewImage(Base):
    __tablename__ = 'reviews_images'

    uuid: Mapped[UUID] = mapped_column(primary_key=True, server_default=text('gen_random_uuid()'))
    review_uuid: Mapped[UUID] = mapped_column(ForeignKey(
        'reviews.uuid',
        ondelete='CASCADE',
        name='reviews_images_review_uuid_fkey'
    ))
    path: Mapped[str]

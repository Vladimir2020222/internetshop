import datetime
import enum
from uuid import UUID

import sqlalchemy
from geoalchemy2 import Geometry
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
    role: Mapped[UserRole] = mapped_column(sqlalchemy.Enum(UserRole), server_default=text("'customer'"))
    warehouse_uuid: Mapped[UUID | None] = mapped_column(
        ForeignKey('warehouses.uuid', name='users_warehouse_uuid_fkey', ondelete='RESTRICT'),
        sqlalchemy.CheckConstraint(
            "(role = 'warehouse_worker') = (warehouse_uuid IS NOT NULL)",
            name='check_warehouse_uuid_with_role'
        )
    )
    delivery_car_uuid: Mapped[UUID | None] = mapped_column(
        ForeignKey('delivery_cars.uuid', name='users_delivery_car_uuid_fkey', ondelete='RESTRICT'),
        sqlalchemy.CheckConstraint(
            "(role = 'courier') = (delivery_car_uuid IS NOT NULL)",
            name='check_delivery_car_uuid_with_role'
        ), unique=True
    )


product_user_association_table = Table(
    'product_user',
    Base.metadata,
    Column('product_uuid', ForeignKey(
        'products.uuid', ondelete='CASCADE', name='product_user_product_uuid_fkey'
    ), primary_key=True),
    Column('user_uuid', ForeignKey(
        'users.uuid', ondelete='CASCADE', name='product_user_user_uuid_fkey'
    ), primary_key=True),
    Column('amount', Integer, nullable=False),
    sqlalchemy.CheckConstraint('amount >= 0', name='check_product_user_amount_positive')
)


product_order_association_table = Table(
    'product_order',
    Base.metadata,
    Column('product_uuid', ForeignKey(
        'products.uuid',
        ondelete='RESTRICT',
        name='product_order_product_uuid_fkey'), primary_key=True),
    Column('order_uuid', ForeignKey(
        'orders.uuid',
        ondelete='CASCADE',
        name='product_order_order_uuid_fkey'), primary_key=True),
    Column('amount', Integer(), nullable=False),
    sqlalchemy.CheckConstraint('amount >= 0', name='check_product_order_amount_positive')
)


product_warehouse_association_table = Table(
    'product_warehouse',
    Base.metadata,
    Column(
        'product_uuid',
        ForeignKey('products.uuid', name='product_warehouse_product_uuid_fkey', ondelete='CASCADE'),
        primary_key=True
    ),
    Column(
        'warehouse_uuid',
        ForeignKey('warehouses.uuid', name='product_warehouse_warehouse_uuid_fkey', ondelete='CASCADE'),
        primary_key=True
    ),
    Column('amount', Integer(), nullable=False),
    sqlalchemy.CheckConstraint('amount >= 0', name='check_product_warehouse_amount_positive')
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
        Integer, sqlalchemy.CheckConstraint('price > 0', name='price_positive')
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


class OrderStatus(enum.Enum):
    collecting = 'collecting'
    delivering = 'delivering'
    done = 'done'
    canceled = 'canceled'
    returning = 'returning'
    returned = 'returned'


class Order(Base):
    __tablename__ = 'orders'

    uuid: Mapped[UUID] = mapped_column(primary_key=True, server_default=text('gen_random_uuid()'))
    user_uuid: Mapped[UUID] = mapped_column(
        ForeignKey('users.uuid', ondelete='RESTRICT', name='orders_user_uuid_fkey')
    )
    status: Mapped[OrderStatus] = mapped_column(sqlalchemy.Enum(OrderStatus))
    # after order is created, price of products might change, but it should not affect price of order. That is why we
    # can't calculate its price based on price of products that is currently in db.
    price: Mapped[int]
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=text('NOW()'))
    deliver_address: Mapped[Geometry] = mapped_column(Geometry(geometry_type='POINT', srid=4326))
    charge_id: Mapped[str] = mapped_column(String(length=100))
    warehouse_uuid: Mapped[UUID] = mapped_column(
        ForeignKey('warehouses.uuid', name='orders_warehouse_uuid_fkey', ondelete='RESTRICT')
    )
    delivery_car_uuid: Mapped[UUID | None] = mapped_column(
        ForeignKey('delivery_cars.uuid', name='orders_delivery_car_uuid_fkey', ondelete='RESTRICT')
    )


class Warehouse(Base):
    __tablename__ = 'warehouses'

    uuid: Mapped[UUID] = mapped_column(primary_key=True, server_default=text('gen_random_uuid()'))
    address: Mapped[Geometry] = mapped_column(Geometry(geometry_type='POINT', srid=4326))


class DeliveryCar(Base):
    __tablename__ = 'delivery_cars'

    uuid: Mapped[UUID] = mapped_column(primary_key=True, server_default=text('gen_random_uuid()'))

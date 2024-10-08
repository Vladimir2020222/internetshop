"""User.delivery_car_uuid field made unique

Revision ID: 6f8e11ba400e
Revises: ffcb2672128f
Create Date: 2024-09-10 19:00:47.337635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f8e11ba400e'
down_revision: Union[str, None] = 'ffcb2672128f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('unique_delivery_car', 'users', ['delivery_car_uuid'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('unique_delivery_car', 'users', type_='unique')
    # ### end Alembic commands ###

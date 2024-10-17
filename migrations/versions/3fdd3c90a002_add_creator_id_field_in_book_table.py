"""Add creator_id field in book table

Revision ID: 3fdd3c90a002
Revises: 46d42cd378af
Create Date: 2024-10-17 14:23:48.301994

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fdd3c90a002'
down_revision: Union[str, None] = '46d42cd378af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('creator_id', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('books', 'creator_id')
    # ### end Alembic commands ###

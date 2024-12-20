"""Add book_id to request table

Revision ID: 2987c7cee068
Revises: 6993ab050dd6
Create Date: 2024-10-23 15:22:21.467530

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2987c7cee068'
down_revision: Union[str, None] = '6993ab050dd6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('requests', sa.Column('book_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'requests', 'books', ['book_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'requests', type_='foreignkey')
    op.drop_column('requests', 'book_id')
    # ### end Alembic commands ###

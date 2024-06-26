"""change played_count from int to str (to save players ids)

Revision ID: 1561b81f9c04
Revises: d17d4e1d7fd4
Create Date: 2024-04-27 19:52:34.621009

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1561b81f9c04'
down_revision: Union[str, None] = 'd17d4e1d7fd4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('game', sa.Column('played_cnt', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('game', 'played_cnt')
    # ### end Alembic commands ###

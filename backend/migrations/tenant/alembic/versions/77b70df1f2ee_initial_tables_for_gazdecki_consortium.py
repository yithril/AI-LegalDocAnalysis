"""Initial tables for gazdecki_consortium

Revision ID: 77b70df1f2ee
Revises: 4eed4cafdd30
Create Date: 2025-07-29 13:23:27.195803

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77b70df1f2ee'
down_revision: Union[str, Sequence[str], None] = '4eed4cafdd30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

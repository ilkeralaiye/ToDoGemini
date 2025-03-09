"""phone number added

Revision ID: ed8fdc7bb13b
Revises: 
Create Date: 2025-03-09 12:07:01.915769

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy


# revision identifiers, used by Alembic.
revision: str = 'ed8fdc7bb13b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sqlalchemy.Column("phoneNumber", sqlalchemy.String, nullable=True))


def downgrade() -> None:
    pass

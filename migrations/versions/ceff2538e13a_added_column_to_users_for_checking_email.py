"""added column to users for checking email

Revision ID: ceff2538e13a
Revises: f031fee53f89
Create Date: 2023-07-24 18:50:52.606319

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ceff2538e13a'
down_revision = 'f031fee53f89'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_verified_email', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_verified_email')
    # ### end Alembic commands ###

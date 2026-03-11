"""add users table

Revision ID: 79fa7008789b
Revises:
Create Date: 2026-03-11 15:23:33.968762

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79fa7008789b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(320), unique=True, nullable=False),
        sa.Column('nombre', sa.String(200), nullable=False, server_default=''),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('plan', sa.String(20), nullable=False, server_default='free'),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                   server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('users')

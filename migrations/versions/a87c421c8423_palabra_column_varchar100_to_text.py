"""palabra column varchar100 to text

Revision ID: a87c421c8423
Revises: 79fa7008789b
Create Date: 2026-03-15 00:12:32.081288

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a87c421c8423'
down_revision = '79fa7008789b'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('palabra', schema=None) as batch_op:
        batch_op.alter_column('palabra',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.Text(),
               existing_nullable=False)


def downgrade():
    with op.batch_alter_table('palabra', schema=None) as batch_op:
        batch_op.alter_column('palabra',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=100),
               existing_nullable=False)

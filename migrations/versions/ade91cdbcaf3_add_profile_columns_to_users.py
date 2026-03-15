"""add profile columns to users

Revision ID: ade91cdbcaf3
Revises: a87c421c8423
Create Date: 2026-03-15 09:38:14.811419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ade91cdbcaf3'
down_revision = 'a87c421c8423'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('birth_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('pais_nacimiento', sa.String(5), nullable=True))
        batch_op.add_column(sa.Column('ciudad_nacimiento', sa.String(200), nullable=True))
        batch_op.add_column(sa.Column('pais_residencia', sa.String(5), nullable=True))
        batch_op.add_column(sa.Column('ciudad_residencia', sa.String(200), nullable=True))
        batch_op.add_column(sa.Column('user_timezone', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('nombre_custom', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('nombre_custom')
        batch_op.drop_column('user_timezone')
        batch_op.drop_column('ciudad_residencia')
        batch_op.drop_column('pais_residencia')
        batch_op.drop_column('ciudad_nacimiento')
        batch_op.drop_column('pais_nacimiento')
        batch_op.drop_column('birth_date')

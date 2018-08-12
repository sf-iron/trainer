"""users table

Revision ID: 8fb428d2fc34
Revises: 
Create Date: 2018-08-11 21:00:52.188241

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8fb428d2fc34'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(), unique=True, nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('activated', sa.Boolean(), default=False),
        sa.Column('activated_at', sa.DateTime(), default=sa.func.now()))


def downgrade():
    op.drop_table('users')

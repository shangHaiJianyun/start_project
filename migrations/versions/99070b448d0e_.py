"""empty message

Revision ID: 99070b448d0e
Revises: 0f4cdff809b0
Create Date: 2018-12-13 14:09:39.857860

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '99070b448d0e'
down_revision = '0f4cdff809b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password', sa.String(length=128), nullable=True))
    op.drop_column('users', 'password_hash')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password_hash', mysql.VARCHAR(length=128), nullable=True))
    op.drop_column('users', 'password')
    # ### end Alembic commands ###

"""empty message

Revision ID: 99e0fa0714ae
Revises: 24c52372af7b
Create Date: 2019-01-03 15:41:39.422381

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '99e0fa0714ae'
down_revision = '24c52372af7b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('areas', 'city_name',
               existing_type=mysql.VARCHAR(length=80),
               nullable=True)
    op.drop_index('area_num', table_name='areas')
    op.drop_index('city_code', table_name='areas')
    op.drop_index('city_name', table_name='areas')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('city_name', 'areas', ['city_name'], unique=True)
    op.create_index('city_code', 'areas', ['city_code'], unique=True)
    op.create_index('area_num', 'areas', ['area_num'], unique=True)
    op.alter_column('areas', 'city_name',
               existing_type=mysql.VARCHAR(length=80),
               nullable=False)
    # ### end Alembic commands ###
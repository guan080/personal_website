"""empty message

Revision ID: c76e3de3cd9a
Revises: None
Create Date: 2016-07-21 23:46:40.100000

"""

# revision identifiers, used by Alembic.
revision = 'c76e3de3cd9a'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'tags', ['name'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tags', type_='unique')
    ### end Alembic commands ###

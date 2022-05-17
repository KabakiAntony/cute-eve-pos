"""initializing the database

Revision ID: d7f48bca1eb3
Revises: 
Create Date: 2022-05-17 16:07:33.520560

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7f48bca1eb3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('User',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_sys_id', sa.String(length=25), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('isActive', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('user_sys_id')
    )
    op.create_table('Action',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('action_sys_id', sa.String(length=25), nullable=False),
    sa.Column('action', sa.String(length=255), nullable=False),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('by', sa.String(length=25), nullable=True),
    sa.ForeignKeyConstraint(['by'], ['User.user_sys_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('action_sys_id')
    )
    op.create_table('Item',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('item_sys_id', sa.String(length=25), nullable=False),
    sa.Column('action_id', sa.String(length=25), nullable=True),
    sa.Column('item', sa.String(length=255), nullable=False),
    sa.Column('units', sa.Numeric(), nullable=False),
    sa.Column('buying_price', sa.Float(), nullable=False),
    sa.Column('selling_price', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['action_id'], ['Action.action_sys_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('item'),
    sa.UniqueConstraint('item_sys_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Item')
    op.drop_table('Action')
    op.drop_table('User')
    # ### end Alembic commands ###
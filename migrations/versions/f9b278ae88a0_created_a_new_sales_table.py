"""created a new sales table

Revision ID: f9b278ae88a0
Revises: b8ddfd03ceb1
Create Date: 2022-08-01 13:22:43.083921

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f9b278ae88a0'
down_revision = 'b8ddfd03ceb1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Sale_Two',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('sale_id', sa.String(length=25), nullable=True),
    sa.Column('item_id', sa.String(length=25), nullable=True),
    sa.Column('buying_price', sa.Float(), nullable=False),
    sa.Column('units', sa.Float(), nullable=False),
    sa.Column('total', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['item_id'], ['Item.item_sys_id'], ),
    sa.ForeignKeyConstraint(['sale_id'], ['Action.action_sys_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Sale',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Sale_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('sale_id', sa.VARCHAR(length=25), autoincrement=False, nullable=True),
    sa.Column('item_id', sa.VARCHAR(length=25), autoincrement=False, nullable=True),
    sa.Column('unit_price', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('units', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('total', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['item_id'], ['Item.item_sys_id'], name='Sale_item_id_fkey'),
    sa.ForeignKeyConstraint(['sale_id'], ['Action.action_sys_id'], name='Sale_sale_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='Sale_pkey')
    )
    op.drop_table('Sale_Two')
    # ### end Alembic commands ###
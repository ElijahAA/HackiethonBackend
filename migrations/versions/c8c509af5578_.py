"""empty message

Revision ID: c8c509af5578
Revises: d124da0264db
Create Date: 2021-04-04 21:42:45.455382

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8c509af5578'
down_revision = 'd124da0264db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('timeline',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.Float(), nullable=True),
    sa.Column('body', sa.String(length=120), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_timeline_timestamp'), 'timeline', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_timeline_timestamp'), table_name='timeline')
    op.drop_table('timeline')
    # ### end Alembic commands ###

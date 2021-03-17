"""empty message

Revision ID: 0f3678996d01
Revises: bba9b254ef3f
Create Date: 2021-03-15 14:59:26.832316

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '0f3678996d01'
down_revision = 'bba9b254ef3f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('multiple_choice_questions', sa.Column('created_at', sa.DateTime(), server_default=func.now()))
    op.create_index(op.f('ix_multiple_choice_questions_created_at'), 'multiple_choice_questions', ['created_at'], unique=False)
    op.add_column('screener_questions', sa.Column('created_at', sa.DateTime(), server_default=func.now()))
    op.create_index(op.f('ix_screener_questions_created_at'), 'screener_questions', ['created_at'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_screener_questions_created_at'), table_name='screener_questions')
    op.drop_column('screener_questions', 'created_at')
    op.drop_index(op.f('ix_multiple_choice_questions_created_at'), table_name='multiple_choice_questions')
    op.drop_column('multiple_choice_questions', 'created_at')
    # ### end Alembic commands ###
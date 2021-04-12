"""empty message

Revision ID: e905c6793ed6
Revises: c94da5da2724
Create Date: 2021-04-12 20:05:46.946597

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e905c6793ed6'
down_revision = 'c94da5da2724'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('paid_projects', 'answer_option_one')
    op.drop_column('paid_projects', 'answer')
    op.drop_column('paid_projects', 'answer_option_three')
    op.drop_column('paid_projects', 'question_id')
    op.drop_column('paid_projects', 'answer_option_two')
    op.drop_column('paid_projects', 'answer_option_five')
    op.drop_column('paid_projects', 'question_type')
    op.drop_column('paid_projects', 'respondent_location')
    op.drop_column('paid_projects', 'question')
    op.drop_column('paid_projects', 'answer_option_four')
    op.drop_column('paid_projects', 'description')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('paid_projects', sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('paid_projects', sa.Column('answer_option_four', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('paid_projects', sa.Column('question', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('paid_projects', sa.Column('respondent_location', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('paid_projects', sa.Column('question_type', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('paid_projects', sa.Column('answer_option_five', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('paid_projects', sa.Column('answer_option_two', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('paid_projects', sa.Column('question_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('paid_projects', sa.Column('answer_option_three', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('paid_projects', sa.Column('answer', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('paid_projects', sa.Column('answer_option_one', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###

"""empty message

Revision ID: c94da5da2724
Revises: 2bae4f431811
Create Date: 2021-04-09 14:10:15.003943

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c94da5da2724'
down_revision = '2bae4f431811'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('u_questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('option_one', sa.String(length=64), nullable=True),
    sa.Column('option_two', sa.String(length=64), nullable=True),
    sa.Column('option_three', sa.String(length=64), nullable=True),
    sa.Column('option_four', sa.String(length=64), nullable=True),
    sa.Column('option_five', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['questions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('u_answers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('option_one_answer', sa.String(length=64), nullable=True),
    sa.Column('option_two_answer', sa.String(length=64), nullable=True),
    sa.Column('option_three_answer', sa.String(length=64), nullable=True),
    sa.Column('option_four_answer', sa.String(length=64), nullable=True),
    sa.Column('option_five_answer', sa.String(length=64), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('u_questions_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['answers.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['u_questions_id'], ['u_questions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_u_answers_option_five_answer'), 'u_answers', ['option_five_answer'], unique=False)
    op.create_index(op.f('ix_u_answers_option_four_answer'), 'u_answers', ['option_four_answer'], unique=False)
    op.create_index(op.f('ix_u_answers_option_one_answer'), 'u_answers', ['option_one_answer'], unique=False)
    op.create_index(op.f('ix_u_answers_option_three_answer'), 'u_answers', ['option_three_answer'], unique=False)
    op.create_index(op.f('ix_u_answers_option_two_answer'), 'u_answers', ['option_two_answer'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_u_answers_option_two_answer'), table_name='u_answers')
    op.drop_index(op.f('ix_u_answers_option_three_answer'), table_name='u_answers')
    op.drop_index(op.f('ix_u_answers_option_one_answer'), table_name='u_answers')
    op.drop_index(op.f('ix_u_answers_option_four_answer'), table_name='u_answers')
    op.drop_index(op.f('ix_u_answers_option_five_answer'), table_name='u_answers')
    op.drop_table('u_answers')
    op.drop_table('u_questions')
    # ### end Alembic commands ###

"""empty message

Revision ID: ffa374086375
Revises: 
Create Date: 2021-01-29 16:46:10.784894

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ffa374086375'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_scale_options_option', table_name='scale_options')
    op.drop_index('ix_scale_options_scale', table_name='scale_options')
    op.drop_table('scale_options')
    op.add_column('answers', sa.Column('location_city', sa.String(), nullable=True))
    op.add_column('answers', sa.Column('location_ip_address', sa.String(), nullable=True))
    op.add_column('answers', sa.Column('location_state', sa.String(), nullable=True))
    op.add_column('answers', sa.Column('multiple_choice_answer_five', sa.String(length=64), nullable=True))
    op.add_column('answers', sa.Column('multiple_choice_answer_four', sa.String(length=64), nullable=True))
    op.add_column('answers', sa.Column('multiple_choice_answer_one', sa.String(length=64), nullable=True))
    op.add_column('answers', sa.Column('multiple_choice_answer_three', sa.String(length=64), nullable=True))
    op.add_column('answers', sa.Column('multiple_choice_answer_two', sa.String(length=64), nullable=True))
    op.add_column('answers', sa.Column('multiple_choice_questions_id', sa.Integer(), nullable=True))
    op.add_column('answers', sa.Column('option_five_answer', sa.String(length=64), nullable=True))
    op.add_column('answers', sa.Column('option_four_answer', sa.String(length=64), nullable=True))
    op.add_column('answers', sa.Column('option_one_answer', sa.String(length=64), nullable=True))
    op.add_column('answers', sa.Column('option_three_answer', sa.String(length=64), nullable=True))
    op.add_column('answers', sa.Column('option_two_answer', sa.String(length=64), nullable=True))
    op.add_column('answers', sa.Column('scale_questions_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_answers_location_city'), 'answers', ['location_city'], unique=False)
    op.create_index(op.f('ix_answers_location_ip_address'), 'answers', ['location_ip_address'], unique=False)
    op.create_index(op.f('ix_answers_location_state'), 'answers', ['location_state'], unique=False)
    op.create_index(op.f('ix_answers_multiple_choice_answer_five'), 'answers', ['multiple_choice_answer_five'], unique=False)
    op.create_index(op.f('ix_answers_multiple_choice_answer_four'), 'answers', ['multiple_choice_answer_four'], unique=False)
    op.create_index(op.f('ix_answers_multiple_choice_answer_one'), 'answers', ['multiple_choice_answer_one'], unique=False)
    op.create_index(op.f('ix_answers_multiple_choice_answer_three'), 'answers', ['multiple_choice_answer_three'], unique=False)
    op.create_index(op.f('ix_answers_multiple_choice_answer_two'), 'answers', ['multiple_choice_answer_two'], unique=False)
    op.create_index(op.f('ix_answers_option_five_answer'), 'answers', ['option_five_answer'], unique=False)
    op.create_index(op.f('ix_answers_option_four_answer'), 'answers', ['option_four_answer'], unique=False)
    op.create_index(op.f('ix_answers_option_one_answer'), 'answers', ['option_one_answer'], unique=False)
    op.create_index(op.f('ix_answers_option_three_answer'), 'answers', ['option_three_answer'], unique=False)
    op.create_index(op.f('ix_answers_option_two_answer'), 'answers', ['option_two_answer'], unique=False)
    op.drop_index('ix_answers_body', table_name='answers')
    op.drop_index('ix_answers_timestamp', table_name='answers')
    op.drop_constraint('answers_question_id_fkey', 'answers', type_='foreignkey')
    op.create_foreign_key(None, 'answers', 'multiple_choice_questions', ['multiple_choice_questions_id'], ['id'])
    op.create_foreign_key(None, 'answers', 'scale_questions', ['scale_questions_id'], ['id'])
    op.drop_column('answers', 'body')
    op.drop_column('answers', 'timestamp')
    op.drop_column('answers', 'question_id')
    op.create_foreign_key(None, 'blog_post_categories', 'blog_posts', ['post_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'blog_post_comments', 'blog_posts', ['post_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'blog_post_tags', 'blog_tags', ['tag_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'blog_post_tags', 'blog_posts', ['post_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('line_items_fk', 'line_items', type_='foreignkey')
    op.create_foreign_key(None, 'line_items', 'screener_questions', ['screener_questions_id'], ['id'])
    op.create_foreign_key(None, 'line_items', 'scale_questions', ['scale_questions_id'], ['id'])
    op.add_column('multiple_choice_answers', sa.Column('multiple_choice_question_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'multiple_choice_answers', 'multiple_choice_questions', ['multiple_choice_question_id'], ['id'], ondelete='CASCADE')
    op.drop_index('ix_project_session', table_name='project')
    op.drop_column('project', 'session')
    op.create_index(op.f('ix_screener_questions_answer_option_one'), 'screener_questions', ['answer_option_one'], unique=False)
    op.create_index(op.f('ix_screener_questions_answer_option_three'), 'screener_questions', ['answer_option_three'], unique=False)
    op.create_index(op.f('ix_screener_questions_answer_option_two'), 'screener_questions', ['answer_option_two'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_screener_questions_answer_option_two'), table_name='screener_questions')
    op.drop_index(op.f('ix_screener_questions_answer_option_three'), table_name='screener_questions')
    op.drop_index(op.f('ix_screener_questions_answer_option_one'), table_name='screener_questions')
    op.add_column('project', sa.Column('session', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.create_index('ix_project_session', 'project', ['session'], unique=False)
    op.drop_constraint(None, 'multiple_choice_answers', type_='foreignkey')
    op.drop_column('multiple_choice_answers', 'multiple_choice_question_id')
    op.drop_constraint(None, 'line_items', type_='foreignkey')
    op.drop_constraint(None, 'line_items', type_='foreignkey')
    op.create_foreign_key('line_items_fk', 'line_items', 'scale_questions', ['screener_questions_id'], ['id'], onupdate='SET DEFAULT', ondelete='SET DEFAULT')
    op.drop_constraint(None, 'blog_post_tags', type_='foreignkey')
    op.drop_constraint(None, 'blog_post_tags', type_='foreignkey')
    op.drop_constraint(None, 'blog_post_comments', type_='foreignkey')
    op.drop_constraint(None, 'blog_post_categories', type_='foreignkey')
    op.add_column('answers', sa.Column('question_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('answers', sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('answers', sa.Column('body', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'answers', type_='foreignkey')
    op.drop_constraint(None, 'answers', type_='foreignkey')
    op.create_foreign_key('answers_question_id_fkey', 'answers', 'questions', ['question_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_answers_timestamp', 'answers', ['timestamp'], unique=False)
    op.create_index('ix_answers_body', 'answers', ['body'], unique=False)
    op.drop_index(op.f('ix_answers_option_two_answer'), table_name='answers')
    op.drop_index(op.f('ix_answers_option_three_answer'), table_name='answers')
    op.drop_index(op.f('ix_answers_option_one_answer'), table_name='answers')
    op.drop_index(op.f('ix_answers_option_four_answer'), table_name='answers')
    op.drop_index(op.f('ix_answers_option_five_answer'), table_name='answers')
    op.drop_index(op.f('ix_answers_multiple_choice_answer_two'), table_name='answers')
    op.drop_index(op.f('ix_answers_multiple_choice_answer_three'), table_name='answers')
    op.drop_index(op.f('ix_answers_multiple_choice_answer_one'), table_name='answers')
    op.drop_index(op.f('ix_answers_multiple_choice_answer_four'), table_name='answers')
    op.drop_index(op.f('ix_answers_multiple_choice_answer_five'), table_name='answers')
    op.drop_index(op.f('ix_answers_location_state'), table_name='answers')
    op.drop_index(op.f('ix_answers_location_ip_address'), table_name='answers')
    op.drop_index(op.f('ix_answers_location_city'), table_name='answers')
    op.drop_column('answers', 'scale_questions_id')
    op.drop_column('answers', 'option_two_answer')
    op.drop_column('answers', 'option_three_answer')
    op.drop_column('answers', 'option_one_answer')
    op.drop_column('answers', 'option_four_answer')
    op.drop_column('answers', 'option_five_answer')
    op.drop_column('answers', 'multiple_choice_questions_id')
    op.drop_column('answers', 'multiple_choice_answer_two')
    op.drop_column('answers', 'multiple_choice_answer_three')
    op.drop_column('answers', 'multiple_choice_answer_one')
    op.drop_column('answers', 'multiple_choice_answer_four')
    op.drop_column('answers', 'multiple_choice_answer_five')
    op.drop_column('answers', 'location_state')
    op.drop_column('answers', 'location_ip_address')
    op.drop_column('answers', 'location_city')
    op.create_table('scale_options',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('scale_questions_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('option', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('scale', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='scale_options_pkey')
    )
    op.create_index('ix_scale_options_scale', 'scale_options', ['scale'], unique=False)
    op.create_index('ix_scale_options_option', 'scale_options', ['option'], unique=False)
    # ### end Alembic commands ###

"""empty message

Revision ID: 2ceb8faaa845
Revises: 6af38803f7dd
Create Date: 2021-05-13 08:52:02.638797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ceb8faaa845'
down_revision = '6af38803f7dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('answers', sa.Column('question_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'answers', 'questions', ['question_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'answers', type_='foreignkey')
    op.drop_column('answers', 'question_id')
    # ### end Alembic commands ###
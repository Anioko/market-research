"""empty message

Revision ID: c570b72392a8
Revises: 1f9184021bb6
Create Date: 2021-05-05 08:22:42.420164

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c570b72392a8'
down_revision = '1f9184021bb6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('answers_user_id_fkey', 'answers', type_='foreignkey')
    op.drop_column('answers', 'user_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('answers', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('answers_user_id_fkey', 'answers', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###
"""empty message

Revision ID: b81dd3212f1a
Revises: e95741a38314
Create Date: 2021-04-21 10:13:34.282207

"""
from alembic import op
import sqlalchemy as sa
import quantumrandom


# revision identifiers, used by Alembic.
revision = 'b81dd3212f1a'
down_revision = 'e95741a38314'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('answers', 'user_no',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.execute(f"UPDATE answers SET user_no = floor(random() * 200 + 1)::int")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('answers', 'user_no',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
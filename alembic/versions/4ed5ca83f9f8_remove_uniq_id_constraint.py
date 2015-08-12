"""Remove uniq_id constraint

Revision ID: 4ed5ca83f9f8
Revises: c5396ed037b
Create Date: 2015-08-12 04:56:37.119931

"""

# revision identifiers, used by Alembic.
revision = '4ed5ca83f9f8'
down_revision = 'c5396ed037b'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import gns
prefix = gns.config.database.prefix
if prefix is None or prefix.upper() is "NONE":
	prefix = ""
gns.prefix = prefix

def upgrade():
    op.drop_constraint("new_courses_uniq_id_key", '{}courses'.format(prefix))

def downgrade():
    pass

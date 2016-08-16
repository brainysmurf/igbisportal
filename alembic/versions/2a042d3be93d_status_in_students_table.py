"""status in students table

Revision ID: 2a042d3be93d
Revises: 19c79fb3eb8a
Create Date: 2016-08-06 03:35:56.409182

"""
# revision identifiers, used by Alembic.
revision = '2a042d3be93d'
down_revision = '19c79fb3eb8a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

import gns
prefix = gns.config.database.prefix
if prefix is None or prefix.upper() is "NONE":
    prefix = ""

def upgrade():
    pass
            
def downgrade():
    pass

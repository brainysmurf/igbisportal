"""add work_email to database

Revision ID: 19c79fb3eb8a
Revises: 5a1d72af2f52
Create Date: 2015-10-08 00:51:53.108986

"""

# revision identifiers, used by Alembic.
revision = '19c79fb3eb8a'
down_revision = '5a1d72af2f52'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

import gns
prefix = gns.config.database.prefix
if prefix is None or prefix.upper() is "NONE":
    prefix = ""

def upgrade():
    op.add_column('{}parents'.format(prefix), 
        sa.Column('work_email', 
            sa.String(255)
            )
        )

def downgrade():
    pass

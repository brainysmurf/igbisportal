"""add igbid to google column

Revision ID: 2e0c73fb3afe
Revises: 185a335dc812
Create Date: 2015-07-25 16:07:06.783843

"""

# revision identifiers, used by Alembic.
revision = '2e0c73fb3afe'
down_revision = '185a335dc812'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import gns
prefix = gns.config.database.prefix
if prefix is None or prefix.upper() is "NONE":
    prefix = ""

def upgrade():
    op.add_column('GoogleSignIn', 
        sa.Column('igbid', 
            sa.BigInteger
            )
        )

def downgrade():
    pass

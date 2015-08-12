"""forgot igbid on users table

Revision ID: c5396ed037b
Revises: 2e0c73fb3afe
Create Date: 2015-07-25 10:00:52.764355

"""

# revision identifiers, used by Alembic.
revision = 'c5396ed037b'
down_revision = '2e0c73fb3afe'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import gns
prefix = gns.config.database.prefix
if prefix is None or prefix.upper() is "NONE":
    prefix = ""

def upgrade():
    op.add_column('{}users'.format(prefix), 
        sa.Column('igbid', 
            sa.BigInteger
            )
        )


def upgrade():
    pass


def downgrade():
    pass

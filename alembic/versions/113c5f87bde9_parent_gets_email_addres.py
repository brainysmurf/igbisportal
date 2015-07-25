"""parent gets email addres

Revision ID: 113c5f87bde9
Revises: 4ca00818f5b3
Create Date: 2015-05-01 16:28:28.834424

"""

# revision identifiers, used by Alembic.
revision = '113c5f87bde9'
down_revision = '4ca00818f5b3'
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
    	sa.Column('email', 
	    	sa.String(255)
	    	)
    	)


def downgrade():
    pass

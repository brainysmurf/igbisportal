"""igbid

Revision ID: 185a335dc812
Revises: 258df7697db7
Create Date: 2015-06-07 12:08:31.981282

"""

# revision identifiers, used by Alembic.
revision = '185a335dc812'
down_revision = '258df7697db7'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import portal.settings as settings
import gns
prefix = settings.get('DATABASE', 'db_prefix')
if prefix is None or prefix.upper() is "NONE":
	prefix = ""
gns.prefix = prefix

def upgrade():
	for gns.account in ['students', 'parents', 'teachers']:
	    op.add_column( gns( '{prefix}{account}' ), 
	    	sa.Column('igbid', 
		    	sa.BigInteger
		    	)
	    	)



def downgrade():
    pass

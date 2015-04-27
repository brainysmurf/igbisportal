"""oops

Revision ID: 4ca00818f5b3
Revises: 34d19f6b9f20
Create Date: 2015-04-27 11:24:20.533045

"""

# revision identifiers, used by Alembic.
revision = '4ca00818f5b3'
down_revision = '34d19f6b9f20'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

import portal.settings as settings
prefix = settings.get('DATABASE', 'db_prefix')


def upgrade():
    op.drop_column('{}students'.format(prefix), 'homeroom_advisors')
    op.add_column('{}students'.format(prefix), 
    	sa.Column('homeroom_advisor', 
	    	sa.BigInteger, 
    		sa.ForeignKey('{}teachers'.format(prefix)+'.id')
    		)
    	)

def downgrade():
    op.drop_column('{}students'.format(prefix), 'homeroom_advisor')

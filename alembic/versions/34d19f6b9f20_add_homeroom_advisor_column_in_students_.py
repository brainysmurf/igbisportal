"""add homeroom_advisor column in students table

Revision ID: 34d19f6b9f20
Revises: 
Create Date: 2015-04-27 18:51:17.469106

"""

# revision identifiers, used by Alembic.
revision = '34d19f6b9f20'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

import portal.settings as settings
prefix = settings.get('DATABASE', 'db_prefix')

def upgrade():
    op.add_column('{}students'.format(prefix), 
    	sa.Column('homeroom_advisors', 
	    	sa.BigInteger, 
    		sa.ForeignKey('{}teachers'.format(prefix)+'.id')
    		)
    	)

def downgrade():
    op.drop_column('{}students', 'homeroom_advisors')

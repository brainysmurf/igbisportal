"""class_grade and archived fields for students

Revision ID: 5a1d72af2f52
Revises: 4ed5ca83f9f8
Create Date: 2015-09-25 02:56:51.140904

"""

# revision identifiers, used by Alembic.
revision = '5a1d72af2f52'
down_revision = '4ed5ca83f9f8'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

import gns
prefix = gns.config.database.prefix
if prefix is None or prefix.upper() is "NONE":
	prefix = ""

def upgrade():
    op.add_column('{}students'.format(prefix), 
        sa.Column('class_grade', 
            sa.String
            )
        )
    op.add_column('{}students'.format(prefix),
    	sa.Column('archived', 
    		sa.Boolean
    		)
    	)

def downgrade():
    pass

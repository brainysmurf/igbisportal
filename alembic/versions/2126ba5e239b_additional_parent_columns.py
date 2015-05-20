"""additional parent columns

Revision ID: 2126ba5e239b
Revises: 113c5f87bde9
Create Date: 2015-05-13 06:35:59.257452

"""

# revision identifiers, used by Alembic.
revision = '2126ba5e239b'
down_revision = '113c5f87bde9'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import portal.settings as settings
prefix = settings.get('DATABASE', 'db_prefix')
if prefix is None or prefix.upper() is "NONE":
    prefix = ""

def upgrade():
    op.add_column('{}parents'.format(prefix), 
        sa.Column('home_phone', 
            sa.String(255)
            )
        )
    op.add_column('{}parents'.format(prefix), 
        sa.Column('mobile_phone', 
            sa.String(255)
            )
        )
    op.add_column('{}parents'.format(prefix), 
        sa.Column('work_phone', 
            sa.String(255)
            )
        )

def downgrade():
    pass

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
import gns
prefix = gns.config.database.prefix
if prefix is None or prefix.upper() is "NONE":
    prefix = ""

def upgrade():
    for column in ['health_information_1_bcg_date', 'health_information_1_dtp_dp_date', 'health_information_1_hepatitis_a_date', 'health_information_1_hepatitis_b_date', 'health_information_1_hib_date', 'health_information_1_immunization_file', 'health_information_1_japanese_b_encephalitis_date', 'health_information_1_mmr_date', 'health_information_1_opv_ipv_date', 'health_information_1_varicella_chicken_pox_date']:

        op.add_column('{}medinfo'.format(prefix), 
            sa.Column(column, 
                sa.String(255)
                )
            )

def downgrade():
    pass

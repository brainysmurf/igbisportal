"""vaccination and health columns

Revision ID: 3e3cdc1dc383
Revises: 2a042d3be93d
Create Date: 2016-08-16 11:04:36.473763

"""

# revision identifiers, used by Alembic.
revision = '3e3cdc1dc383'
down_revision = '2a042d3be93d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

import gns
prefix = gns.config.database.prefix
if prefix is None or prefix.upper() is "NONE":
	prefix = ""

def upgrade():
    for column in ['immunization_record_1_bcg_date', 'immunization_record_1_dtp_dp_date', 'immunization_record_1_hepatitis_a_date', 'immunization_record_1_hepatitis_b_date', 'immunization_record_1_hib_date', 'immunization_record_1_immunization_file', 'immunization_record_1_japanese_b_encephalitis_date', 'immunization_record_1_mmr_date', 'immunization_record_1_opv_ipv_date', 'immunization_record_1_varicella_chicken_pox_date']:
        op.add_column('{}medinfo'.format(prefix), 
            sa.Column(column, 
                sa.String(255)
                )
            )


def downgrade():
    pass

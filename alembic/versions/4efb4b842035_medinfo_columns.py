"""medinfo columns

Revision ID: 4efb4b842035
Revises: 3e3cdc1dc383
Create Date: 2016-08-16 15:34:25.657592

"""

# revision identifiers, used by Alembic.
revision = '4efb4b842035'
down_revision = '3e3cdc1dc383'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

import gns
prefix = gns.config.database.prefix
if prefix is None or prefix.upper() is "NONE":
    prefix = ""



def upgrade():

    print('upgrade')
    for column in ['emergency_contact_1_email', 'emergency_contact_2_title', 'immunization_record_2_hepatitis_a_question', 'emergency_contact_4_email', 'emergency_contact_3_e_mail_address', 'emergency_contact_3_email', 'immunization_record_2_mmr_question', 'emergency_contact_1_e_mail_address', 'immunization_record_2_bcg_question', 'emergency_contact_2_prefix', 'immunization_record_1_opv_ipv_question', 'immunization_record_1_bcg_question', 'emergency_contact_4_title', 'immunization_record_2_varicella_chicken_pox_question', 'health_information_1_disorders', 'immunization_record_1_hib_question', 'immunization_record_1_japanese_b_encephalitis_question', 'immunization_record_1_varicella_chicken_pox_question', 'immunization_record_2_hib_question', 'immunization_record_2_dtp_dp_question', 'immunization_record_2_hepatitis_b_date', 'emergency_contact_1_title', 'immunization_record_1_hepatitis_a_question', 'immunization_record_2_japanese_b_encephalitis_date', 'immunization_record_2_varicella_chicken_pox_date', 'immunization_record_2_opv_ipv_date', 'emergency_contact_2_ec_relationship', 'immunization_record_2_dtp_dp_date', 'immunization_record_2_mmr_date', 'immunization_record_2_bcg_date', 'immunization_record_2_japanese_b_encephalitis_question', 'emergency_contact_1_prefix', 'immunization_record_1_mmr_question', 'emergency_contact_3_title', 'immunization_record_2_hepatitis_a_date', 'emergency_contact_1_ec_relationship', 'emergency_contact_2_e_mail_address', 'immunization_record_1_dtp_dp_question', 'immunization_record_2_opv_ipv_question', 'emergency_contact_3_prefix', 'immunization_record_2_immunization_file', 'immunization_record_2_hib_date', 'emergency_contact_3_ec_relationship', 'immunization_record_1_hepatitis_b_question', 'immunization_record_2_hepatitis_b_question', 'emergency_contact_2_email']:
        op.add_column('{}medinfo'.format(prefix), 
            sa.Column(column, 
                sa.String(255)
                )
            )

def downgrade():
    pass

if __name__ == "__main__":
    print("GO")
    upgrade()
    print("DONE")
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.cr.execute("""
        UPDATE res_partner
        SET vat = academic_identification_number
        WHERE (vat IS NULL OR vat = '')
        AND academic_identification_number IS NOT NULL
        AND academic_identification_number != ''
    """)
    env.cr.execute("""
        UPDATE res_partner
        SET vat = NULL
        WHERE partner_type = 'family'
    """)

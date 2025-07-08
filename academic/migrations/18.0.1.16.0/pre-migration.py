from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='res_partner'
        AND column_name='academic_identification_number'
    """)
    if env.cr.fetchone():
        env.cr.execute("ALTER TABLE res_partner DROP COLUMN academic_identification_number")

    openupgrade.rename_fields(
        env,
        [
            (
                "res.partner",
                "res_partner",
                "dni",
                "academic_identification_number",
            ),
        ],
    )

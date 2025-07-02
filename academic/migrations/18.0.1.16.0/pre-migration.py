from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
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

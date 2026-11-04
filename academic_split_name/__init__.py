# © 2016 ADHOC SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from . import models


def post_init_hook(env):
    """Fill the parts of the academic contacts that already exist.

    The parts used to be computed fields, so installing the module filled them
    on its own; now they are plain columns and the split only runs on write.
    """
    partners = env["res.partner"].search(
        [
            ("partner_type", "in", ["student", "parent", "family"]),
            ("firstname", "=", False),
            ("middlename", "=", False),
            ("lastname", "=", False),
            ("second_lastname", "=", False),
            ("name", "!=", False),
        ]
    )
    for partner in partners:
        parts = partner._parts_from_name(partner.name, partner.partner_type)
        if parts:
            partner.write(parts)

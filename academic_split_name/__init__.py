# © 2016 ADHOC SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from . import models


def post_init_hook(env):
    """Fill the parts of the academic contacts that already exist.

    The parts used to be computed fields, so installing the module filled them
    on its own; now they are plain columns and the split only runs on write.

    It takes the contacts without a last name -- the part the form requires for
    the three academic types -- and not only the ones with the four parts
    empty, which leaves out a contact that already carries one of the other
    two. The four parts are written from the name, so the name never changes.
    """
    partners = env["res.partner"].search(
        [
            ("partner_type", "in", ["student", "parent", "family"]),
            ("lastname", "=", False),
            ("name", "!=", False),
        ]
    )
    for partner in partners:
        parts = partner._parts_from_name(partner.name, partner.partner_type)
        if parts:
            partner.write(parts)

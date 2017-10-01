# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):

    xmlid_renames = [
        ('base.group_portal_parent',
            'portal_academic.group_portal_parent',),
        ('base.group_portal_teacher',
            'portal_academic.group_portal_teacher',),
        ('base.group_portal_administrator',
            'portal_academic.group_portal_administrator',),
        ('base.group_portal_gral_administrator',
            'portal_academic.group_portal_gral_administrator',),
    ]
    openupgrade.rename_xmlids(cr, xmlid_renames)

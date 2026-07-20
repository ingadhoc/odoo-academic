# © 2016 ADHOC SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Demo Academic",
    "version": "18.0.1.1.0",
    "sequence": 14,
    "summary": "",
    "author": "ADHOC SA",
    "website": "www.adhoc.com.ar",
    "license": "AGPL-3",
    "depends": [
        "academic_sale_subscription",
        "sale_subscription_loyalty_ux",
        "sale_loyalty_ux",
    ],
    "demo": [
        "demo/res_partner_category.xml",
        "demo/loyalty_program.xml",
        "demo/loyalty_rule.xml",
        "demo/product_pricelist.xml",
        "demo/res_partner_updates.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}

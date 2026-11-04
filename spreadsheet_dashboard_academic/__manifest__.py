# © 2016 ADHOC SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Spreadsheet Dashboard Academic",
    "version": "20.0.1.0.0",
    "sequence": 14,
    "summary": "Academic Spreadsheet Dashboard for Invoice Tracking",
    "author": "ADHOC SA",
    "website": "www.adhoc.com.ar",
    "license": "LGPL-3",
    "category": "Academic",
    "depends": [
        "academic_sale_subscription",
        "account_internal_transfer",
        "spreadsheet_dashboard",
    ],
    "data": [
        "data/dashboards.xml",
    ],
    "installable": True,
    "auto_install": ["academic_sale_subscription"],
    "application": False,
}

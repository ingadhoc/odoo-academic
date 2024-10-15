# © 2016 ADHOC SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Academic Sale Subscription',
    'version': "17.0.1.0.0",
    'sequence': 14,
    'summary': '',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'depends': [
        'academic',
        'sale_subscription'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_template_views.xml',
        'views/sale_order_views.xml',
        # 'wizard/reenrollment_views.xml'
        'views/sale_subscription_plan_views.xml',
        'wizard/academic_order_wizard_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

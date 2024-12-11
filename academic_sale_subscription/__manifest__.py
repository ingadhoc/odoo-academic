# © 2016 ADHOC SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Academic Sale Subscription',
<<<<<<< HEAD
    'version': "18.0.1.0.0",
||||||| parent of 6923882 (temp)
    'version': "17.0.1.1.0",
=======
    'version': "17.0.1.2.0",
>>>>>>> 6923882 (temp)
    'sequence': 14,
    'summary': '',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'depends': [
        'academic',
        'sale_subscription_ux'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_template_views.xml',
        'views/sale_order_views.xml',
        'views/sale_subscription_plan_views.xml',
        'wizard/academic_order_wizard_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

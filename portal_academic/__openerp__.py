# -*- coding: utf-8 -*-
{
    'author': 'Sistemas ADHOC',
    'auto_install': True,
    'installable': True,
    'category': 'Tools',
    'demo': [
        'data/demo/res_users.xml',
        'data/demo/res.partner.csv',
    ],
    'depends': ['portal', 'academic'],
    'description': 'Academic Portal',
    'init_xml': [],
    'license': 'AGPL-3',
    'name': u'Academic Portal',
    'test': [],
    'data': [
        'security/portal_academic_security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'portal_evaluation_view.xml',
    ],
    'version': '1.1',
    'website': ''}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

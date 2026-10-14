# -*- coding: utf-8 -*-

{
    'name': 'Payment transfer - Account',
    'category': 'Accounting/Accounting',
    'summary': 'Internal Transfer for Cash and Bank Payments',
    'version': '1.0',
    'description': """Add internal transfer option to cash and bank payments""",
    'author': "Parfait BENE MANGA",
    'website': "http://www.parfaitbene.com",
    'depends': ['payment'],
    'data': [
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

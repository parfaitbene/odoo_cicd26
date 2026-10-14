# -*- coding: utf-8 -*-
{
    'name': "Caisse CM",

    'summary': """
        Adds new features and constraints to cash box.""",

    'description': """
    """,

    'author': "Parfait BENE MANGA",
    'website': "http://www.parfaitbene.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/company_type_operation.xml',
        'views/account_payment.xml',
        'views/res_partner.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}

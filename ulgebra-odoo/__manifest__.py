# -*- coding: utf-8 -*-
{
    'name': "Ulgebra - API",

    'summary': "Ulgebra - API",

    'description': "Long description of module's purpose",

    'author': "Ulgebra",

    'website': "https://sms.ulgebra.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'event'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/app_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'auto_install': True,
    'installable': True,
    'application': False
}


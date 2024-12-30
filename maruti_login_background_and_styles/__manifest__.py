# -*- encoding: utf-8 -*-
{
    'name': 'Login Background And Styles',
    'summary': 'The new configurable Odoo Web Login Screen',
    'version': '17.0.2.0.0',
    'category': 'website',
    'summary': """
    You can customised login page like add background image or color and change position of login form.
    """,
    'author': 'Maruti Softserv',
    'website': 'https://marutisoftserv.com/',
    'license': 'AGPL-3',
    'depends': ['base', 'base_setup', 'web', 'auth_signup'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/login_image.xml',
        'templates/left_login_template.xml',
        'templates/right_login_template.xml',
        'templates/middle_login_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'maruti_login_background_and_styles/static/src/css/web_login_style.css',
        ]
    },
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'images': ['static/description/banner.png'],
    'price': '0.00'
}

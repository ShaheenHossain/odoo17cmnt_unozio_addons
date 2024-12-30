{
    'name': 'Disable Right Click',
    'version': '17.0',
    'summary': 'Disables right-click functionality on specific pages',
    'description': """
    This module disables the right-click functionality on specific pages.
    """,
    'category': 'website',
    'author': 'Devendra kavthekar',
    "support": "dkatodoo@gmail.com",
    "website": "https://dek-odoo.github.io",
    "license": "OPL-1",
    "images": ["static/description/banner.gif"],
    "price": 0.00,
    "currency": "EUR",

    'depends': ['base','website'],
    
    'data': [
        'views/website_settings_views.xml',
    ],
    'assets':{
        'web.assets_frontend': [
            'deskent_website_disable_right_click/static/src/js/disable_right_click.js',
            'deskent_website_disable_right_click/static/src/js/sweetalert2.js',
            ],
        'web.assets_backend': [
            'deskent_website_disable_right_click/static/src/css/setting_box.css',
            ]
    },
    'qweb': [],
    
    'installable': True,
    'application': False,
    'auto_install': False, 

} 

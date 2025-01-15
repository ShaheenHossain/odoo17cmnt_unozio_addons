# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Email Validation Widget(OWl Javascript)',
    'version': '1.0',
    'category': 'General',
    'description': """Email Validation Widget(OWl Javascript)""",
    'company': 'Tech4Logic',
    'website': 'https://tech4logic.wordpress.com/',
    'author': 'Arun Reghu Kumar',
    'depends' : ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',      
    ],
    'assets': {
        'web.assets_backend': [
            'email_validation_widget/static/src/components/*/*.js',
            'email_validation_widget/static/src/components/*/*.xml',
            'email_validation_widget/static/src/components/*/*.scss',
        ],
    },
    'demo': [
    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

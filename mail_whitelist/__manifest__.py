{
    'name': 'Mail Whitelist',
    'version': '17.0.1.0.0',
    'summary': "Mail Whitelist",
    'description': """
    Define white list of emails to prevent undesired email activity during development/testing.
    """,
    'author': 'Opsway',
    'category': 'Productivity/Discuss',
    'depends': ['mail'],
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_mail_server_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}

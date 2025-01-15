# Copyright © 2024
# @author: Sergii Mozolevskyi (<mozolevskyi2010@gmail.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

{
    'name': 'Unique e-mail contacts',
    'version': '17.0.1.0.0',
    'description': 'A module that adds functionality that '
                   'does not allow having several partners '
                   'with the same e-mail in the system.',
    'author': 'Sergii Mozolevskyi',
    'category': 'Extra Tools',
    'license': 'LGPL-3',

    'depends': [
        'base',
    ],

    'summary': 'A module that adds functionality that '
               'does not allow having several partners '
               'with the same e-mail in the system.',
    'support': 'mozolevskyi2010@gmail.com',

    'external_dependencies': {
        'python': [],
    },

    'images': [
        'static/description/icon.png', 'static/description/banner.png'
    ],

    'application': False,
    'installable': True,
    'auto_install': False,
}

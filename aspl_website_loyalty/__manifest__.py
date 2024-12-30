# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'Website Loyalty (Community)',
    'category': 'Website of Sale',
    'summary': 'This module allows customers earn loyalty points.',
    'description': """This module allows customers earn loyalty points.""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'version': '17.0.1.0.0',
    'price': 0,
    'currency': 'EUR',
    'depends': ['base', 'website_sale'],
    "data": [
        'security/ir.model.access.csv',
        'data/reward_product.xml',
        'data/loyalty_sequence.xml',
        'views/loyalty_view.xml',
        'views/res_config_settings_view.xml',
        'views/res_partner_view.xml',
        'views/loyalty_reward.xml',
        'views/sale_order_view.xml',
    ],
    'assets': {
         'web.assets_frontend': [
            '/aspl_website_loyalty/static/src/js/main.js'
         ]
    },
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

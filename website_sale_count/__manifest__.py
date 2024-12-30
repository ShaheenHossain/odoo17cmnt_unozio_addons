# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Sale Count',
    'version': '17.0.0.0',
    'category': 'eCommerce',
    'license':'LGPL-3',
    'summary': 'Shows Sales/Puchases Counter on website/Shop Page',
    'description': 'This module allows to display the Total Number of Products Sales Count in the Website.Sales Count on website, Website Sales count, Webshop sales couunt, Sale Count on Webshop, Show sales counter on shop page, purchase counter on shop page, Sales counter on website, Purchase counter on website, show number of sales on website, sales number on website, show number of sales on shop, sales number on shop',
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    'depends': ['website','website_sale','product'],
    'data': [
        'views/template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_sale_count/static/src/js/product_sale_count.js',
        ],
       
    },
    'application': True,
    'installable': True,
    'live_test_url':'https://youtu.be/kqvC_S1m1CA',
    "images":['static/description/Banner.gif'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

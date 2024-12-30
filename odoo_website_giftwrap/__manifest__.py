# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Website Gift Product Wrap/Packing Odoo",
    "version" : "17.0.0.2",
    "category" : "eCommerce",
    "depends" : ['website','website_sale','sale_management'],
    "author": "BROWSEINFO",
    "license" :"OPL-1",
    "summary": 'Apps helps to Add Gift Wrap for product on Odoo eCommerce Website Gift Wrap product shop Gift Wrap Gift package on webshop gift Website Gift pack webshop Gift Wrap product Gift pack website gift card shop gift wrap item gift wrap for website ',
    "description": """
        Website Gift Wrap
        Website Gift pack
        Gift Wrap on website
        Gift pack on website
        Gift package on website
        
        webshop Gift Wrap
        webshop Gift pack
        Gift Wrap on webshop
        Gift pack on webshop
        Gift package on webshop
        
        
        shop Gift Wrap
        shop Gift pack
        website Gift Wrap on shop
        website Gift pack on shop
        website Gift package on shop
        website gift packing website
        website gift card website
       
        
    """,
    'website': "https://www.browseinfo.com/demo-request?app=odoo_website_giftwrap&version=17&edition=Community",
    "data": [
        'security/ir.model.access.csv',
        'views/giftwrap.xml',
        'views/template.xml',
        'views/journal_template.xml',

    ],
    
    "auto_install": False,
    "application": True,
    "installable": True,
    'live_test_url': 'https://www.browseinfo.com/demo-request?app=odoo_website_giftwrap&version=17&edition=Community',
    "images":["static/description/Banner.gif"],
    'assets':{
        'web.assets_frontend':[
        'odoo_website_giftwrap/static/src/css/custom.css',
        'odoo_website_giftwrap/static/src/js/custom.js',
        ]
    },
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

{
    "name": "Odoo Shopify Integration",

    "summary": "This Odoo Shopify connector streamlines daily operations for warehouse and sales teams through automation, enhancing efficiency and simplifying processes. , Odoo Shopify Integration, Shopify Connector for Odoo, Warehouse Automation, Sales Automation Tool, Shopify Order Synchronization, Inventory Sync Between Odoo and Shopify, Automated Inventory Management, Shopify Sales Data Integration, Warehouse Management Solution, Real-Time Data Sync, Shopify-Odoo Workflow Automation, Order Fulfillment Automation, Inventory Tracking System, Shopify Integration Module, Seamless Shopify-Odoo Connection, Automated Stock Updates, Shopify Sales Sync, Odoo Shopify ERP Integration, Multi-Channel Sales Management, Shopify Data Automation Tool",

    "category": "website",

    "version": "17.0",

    "author": "INKERP",

    "website": "http://www.inkerp.com",

    "depends": ["eg_ecommerce_base", "product"],

    "data": [
        'security/ir.model.access.csv',
        'data/ir_sequence_view.xml',
        'data/action_server_view.xml',
        'data/ir_cron_view.xml',
        'wizards/export_product_shopify_wizard_view.xml',
        'wizards/import_from_ecom_provider_view.xml',
        'views/res_config_settings_view.xml',
        'views/account_move_view.xml',
        'views/eg_ecom_instance_view.xml',
        'views/sale_order_view.xml',
    ],

    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}

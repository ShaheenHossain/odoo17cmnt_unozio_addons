# -*- coding: utf-8 -*-
{
    'name': "Twilio SMS",

    'summary': "Twilio SMS by Ulgebra. Send SMS, Manage SMS History and Sync Incoming messages to CRM modules as records",

    'description': """Connect with multiple contacts at once by sending Twilio messages using predefined message templates. Send media files such as images, videos and documents as attachments.Instantly send proactive messages to customers using the Twilio extension window which to avoid any delay in your communications. Stay up to date with the Twilio conversations with the help of real-time notifications and desktop notifications. Maintain the record of all Twilio conversations held and view complete chats whenever required. You can also reach out to us for this integration setup. 
    Need more apps or assistance? Visit our website or contact our support team for live help at https://sms.ulgebra.com. """,

    'author': "Ulgebra",
    'maintainer': "Ulgebra",
    'website': "https://sms.ulgebra.com",
    "support": "support@ulgebra.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'SMS and Whatsapp',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm', 'ulgebra-odoo'],
    'images': ['static/description/logo.png'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/app_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}


# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': "Print Email and Messages PDF Report",
    'version': '17.0.0.0',
    'category': 'Extra Tools',
    'summary': "Print Email and Message Odoo App helps users to printing the emails and messages in report print email pdf report print message pdf report print email report print message report print message and email print email and messages reports",
    'description': """
         This module helps users to printing the emails and messages in report. In emails and messages there would be an option to take a print email template and message template in PDF format. 
    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    'depends': ['base', 'sale_management', 'purchase', 'account'],
    'data': [
         'report/email_report_action.xml',
         'report/email_report_template.xml',
         'report/message_report_template.xml',
         'report/messge_report_action.xml',
    ],
    'license':'LGPL-3',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/fg2lDggYDkc',
    "images":['static/description/Banner.gif'],
}

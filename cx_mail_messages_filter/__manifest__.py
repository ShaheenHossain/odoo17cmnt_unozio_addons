###################################################################################
#
#    Copyright (C) 2020 Cetmix OÜ
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

{
    "name": "Message Filter Anti spam Filter messages Spam protection",
    "version": "17.0.1.0.4",
    "summary": "Filter messages using custom filters. Spam protection",
    "author": "Cetmix",
    "license": "LGPL-3",
    "price": 0.00,
    "currency": "EUR",
    "category": "Discuss",
    "website": "https://cetmix.com",
    "live_test_url": "https://demo.cetmix.com",
    "images": ["static/description/banner.png"],
    "depends": ["prt_mail_messages"],
    "demo": [
        "data/demo.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mail_message.xml",
        "views/cx_messages_filter_view.xml",
        "views/actions.xml",
        "views/mail_alias_view.xml",
        "data/cron.xml",
        "views/res_config_settings.xml",
    ],
    "qweb": [],
    "installable": True,
    "application": False,
}

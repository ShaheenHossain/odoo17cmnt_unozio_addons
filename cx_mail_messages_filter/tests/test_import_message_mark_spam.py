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

from odoo.tests import Form, TransactionCase


class TestMarkSpamIncomingMessage(TransactionCase):
    def setUp(self):
        super().setUp()
        form = Form(self.env["cx.message.filter"])
        form.name = "Test Spam Filter"
        form.action = "x"
        with form.rule_ids.new() as rule, rule.condition_ids.new() as item:
            item.trigger = "from"
            item.condition = "like"
            item.value = "example@exmpl.com"
        self.cx_message_filter_spam_test_1 = form.save()
        self.cx_message_filter_spam_test_1.order = 1
        self.msg_dict = {
            "message_type": "email",
            "message_id": "",
            "subject": "Mail Test Subject",
            "from": "Test User Example <example@exmpl.com>",
            "to": "demo5@example.com, "
            "Test User <test1@example.com>, "
            "demo6@example.com",
            "cc": "",
            "email_from": "Test1 User1 <example@exmpl.com>",
            "date": "2021-08-04 15:08:08",
            "body": '<div dir="ltr"><span>DATA Text</span><br></div>',
            "attachments": [],
            "author_id": 1,
        }

    def test_move_to_spam(self):
        result = self.env["cx.message.filter"].message_new(
            self.msg_dict, custom_values=None
        )
        self.assertEqual(
            result.id, self.cx_message_filter_spam_test_1.id, msg="Filter must be spam"
        )
        self.assertEqual(result.action, "x", msg="Filter action must be equal to 'x'")
        self.assertTrue(result.active, msg="Filter must be active")

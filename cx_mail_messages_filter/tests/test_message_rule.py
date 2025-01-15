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

from odoo.tests import Form

from .common import MailMessagesFilterCommon


class TestFilterRule(MailMessagesFilterCommon):
    def setUp(self):
        super().setUp()
        form = Form(self.env["cx.message.filter"])
        form.name = "Test Filter #1"
        form.action = "m"
        form.destination_model_id = self.ir_model_res_partner
        with form.rule_ids.new() as rule:
            with rule.condition_ids.new() as item:
                item.trigger = "recipients"
                item.partner_ids.add(self.res_partner_bob)
            with rule.condition_ids.new() as item:
                item.trigger = "author"
                item.partner_ids.add(self.res_partner_bob)
        with form.rule_ids.new() as rule:
            with rule.condition_ids.new() as item:
                item.trigger = "from"
                item.value = "test@example.com"
            with rule.condition_ids.new() as item:
                item.trigger = "subject"
                item.value = "Test Subject"
        self.filter = form.save()

        form = Form(self.env["cx.message.filter"])
        form.name = "Test Filter #2"
        form.action = "m"
        form.destination_model_id = self.ir_model_res_partner
        self.filter_2 = form.save()

        self.msg_dict = {
            "message_type": "email",
            "message_id": "",
            "subject": "Mail Test Subject",
            "to": "demo5@example.com, "
            "Test User <test1@example.com>, "
            "demo6@example.com",
            "cc": "",
            "email_from": "Test1 User1 <demo7@exmaple.com>",
            "date": "2021-08-04 15:08:08",
            "body": '<div dir="ltr"><span>DATA Text</span><br></div>',
            "attachments": [],
            "author_id": 1,
        }

    def test_check_conditions(self):
        valid_msg_dict = {
            **self.msg_dict,
            "from": "Test User Example <test@example.com>",
        }
        invalid_msg_dict = {
            **self.msg_dict,
            "from": "Test1 User1 <demo7@exmaple.com>",
        }

        result_valid = self.filter.rule_ids.check_conditions(valid_msg_dict)
        self.assertTrue(result_valid, msg="Condition result must be True")

        result_invalid = self.filter.rule_ids.check_conditions(invalid_msg_dict)
        self.assertFalse(result_invalid, msg="Condition result must be False")

        result_invalid = self.filter_2.rule_ids.check_conditions(valid_msg_dict)
        self.assertFalse(result_invalid, msg="Condition result must be False")

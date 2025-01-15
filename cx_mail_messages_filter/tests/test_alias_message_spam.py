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

from odoo.tests import common


class TestSpamAlias(common.TransactionCase):
    """
    TEST 1 : Mark Spam message by alias
        [Create message by function '_message_route_process']
        - message record_ref is spam filter
        - message message_filter_id not empty and equal spam filter
        - message spam_date not False
        - message active is False
    """

    def setUp(self):
        super().setUp()
        mail_alias_obj = self.env["mail.alias"]
        cx_message_filter_obj = self.env["cx.message.filter"]
        cx_message_filter_rule_obj = self.env["cx.message.filter.rule"]
        self.test_ir_model_filter = self.env.ref(
            "cx_mail_messages_filter.model_cx_message_filter"
        )

        self.mail_alias_test = mail_alias_obj.create(
            {
                "alias_name": "test_example",
                "alias_model_id": self.test_ir_model_filter.id,
                "alias_contact": "everyone",
                "check_spam": True,
            }
        )

        self.cx_message_filter_test_1 = cx_message_filter_obj.create(
            {
                "active": True,
                "name": "Test Spam Filter #1",
                "action": "x",
            }
        )

        self.cx_message_filter_rule_test = cx_message_filter_rule_obj.create(
            {"filter_id": self.cx_message_filter_test_1.id}
        )

        self.cx_message_filter_rule_test.condition_ids.create(
            {
                "rule_id": self.cx_message_filter_rule_test.id,
                "trigger": "from",
                "condition": "is",
                "value": "from_test_example@example.com",
            }
        )
        self.message_dict = {
            "message_type": "email",
            "message_id": "<CABFLKGmak@mail.example.com>",
            "subject": "DATA",
            "email_from": '"FROM_Test Example" <from_test_example@example.com>',
            "from": '"FROM_Test Example" <from_test_example@example.com>',
            "cc": "",
            "recipients": "test_example@example.com,"
            '"Test Example" <test_example@example.com>',
            "to": 'test_example@example.com,"Test Example" <test_example@example.com>',
            "partner_ids": [],
            "references": "",
            "in_reply_to": "",
            "date": "2022-02-17 08:34:38",
            "body": '<div dir="ltr">TEST DATA<br></div>\n',
            "attachments": [],
            "bounced_email": False,
            "bounced_partner": self.env["res.partner"],
            "bounced_message": self.env["mail.message"],
            "author_id": False,
        }
        self.routes = [("cx.message.filter", 0, {}, 2, self.mail_alias_test)]

    def test_alias_spam_filter(self):
        thread_id = self.env["cx.message.filter"]._message_route_process(
            "", self.message_dict, self.routes
        )

        self.assertEqual(
            thread_id,
            self.cx_message_filter_test_1.id,
            msg=f"Thread ID must be equal to {self.cx_message_filter_test_1.id}",
        )

        message_id = self.env["mail.message"].search(
            [
                ("active", "=", False),
                ("message_filter_id", "=", self.cx_message_filter_test_1.id),
            ],
            limit=1,
        )
        self.assertEqual(
            message_id.record_ref.id,
            self.cx_message_filter_test_1.id,
            msg="Record ref must be id equal 'cx_message_filter_test_1'",
        )
        self.assertEqual(
            message_id.message_filter_id,
            self.cx_message_filter_test_1,
            msg="Filter id must be equal 'cx_message_filter_test_1'",
        )
        self.assertNotEqual(
            message_id.spam_date, False, msg="Spam Datetime must not be empty"
        )
        self.assertFalse(message_id.active, msg="Message active must be False")

    def test_alias_without_span_filter(self):
        default_filter_id = self.ref(
            "cx_mail_messages_filter.cx_message_filter_test_002"
        )
        self.env["cx.message.filter"].search(
            [
                ("active", "=", True),
                ("action", "=", "x"),
            ],
        ).unlink()
        thread_id = self.env["cx.message.filter"]._message_route_process(
            "", self.message_dict, self.routes
        )
        self.assertEqual(
            thread_id,
            default_filter_id,
            msg=f"Message filter ID must be equal to {default_filter_id}",
        )
        message = self.env["mail.message"].search(
            [
                ("subject", "=", "DATA"),
                ("message_filter_id", "=", default_filter_id),
            ],
            limit=1,
        )
        self.assertTrue(message.exists(), msg="Message must exist")
        self.assertFalse(message.spam_date, msg="Message must not be spam")

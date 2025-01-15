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

from odoo.exceptions import UserError
from odoo.tests import Form

from .common import MailMessagesFilterCommon


class TestFilterCondition(MailMessagesFilterCommon):
    """
    TEST 1 : Create invalid condition
        [Create invalid condition 'is']
        - has an exception
    TEST 2 : Create valid conversation and change conversation
        [Update condition 'not']
        - has an exception
    TEST 3 : Test function condition_other
        [Create condition 'is']
        - email 'bob@example.co' is valid
        - email 'mr.bob@example.co' is invalid
        - email 'superbob@emample.com' is invalid
        [Create condition 'not']
        - email 'bob@example.co' is invalid
        - email 'mr.bob@example.co' is valid
        - email 'superbob@emample.com' is valid
        - email 'example@exmpl.com' is valid
    TEST 4 : Create condition for message in spam filter
        [Create filter #1, message]
        [Mark spam message]
        - message filter id is filter id #1
        - filter #1 has condition with ("from", "is", "partner_email")
    TEST 5 : Create spam filter with condition. Create message and it marks to spam.
        [Create filter #1, rule, condition]
        condition: ("from" "is" "partner_email")
        [Create message]
        [Mark spam]
        - message_filter_id  is filter #1

    """

    def setUp(self):
        super().setUp()
        cx_message_filter_obj = self.env["cx.message.filter"]

        self.mail_message_test_1 = self.env["mail.message"].create(
            {
                "subject": "Test Message #1",
                "body": "Test with no html text",
                "email_from": self.res_partner_bob.email,
                "author_id": self.res_partner_bob.id,
            }
        )

        form = Form(cx_message_filter_obj)
        form.name = "Test Filter #1"
        form.action = "m"
        form.destination_model_id = self.env.ref("base.model_res_partner")
        with form.rule_ids.new() as line, line.condition_ids.new() as item:
            item.trigger = "author"
            item.condition = "like"
            item.partner_ids.add(self.res_partner_bob)
        self.cx_message_filter_test_1 = form.save()

        self.cx_message_filter_rule_test_1 = self.cx_message_filter_test_1.rule_ids[0]

        form = Form(cx_message_filter_obj)
        form.name = "Test Spam Filter"
        form.action = "x"
        self.cx_message_filter_spam_test_1 = form.save()
        self.cx_message_filter_spam_test_1.order = 1

    def test_invalid_condition(self):
        with self.assertRaises(UserError):
            with Form(self.cx_message_filter_test_1) as form, form.rule_ids.edit(
                0
            ) as rule, rule.condition_ids.new() as item:
                item.trigger = "author"
                item.condition = "is"
                item.partner_ids.add(self.res_partner_bob)

    def test_update_condition(self):
        with self.assertRaises(UserError):
            with Form(self.cx_message_filter_test_1) as form, form.rule_ids.edit(
                0
            ) as rule, rule.condition_ids.edit(0) as item:
                item.condition = "not"

    def test_condition_other(self):
        with Form(self.cx_message_filter_test_1) as form, form.rule_ids.edit(
            0
        ) as rule, rule.condition_ids.new() as item:
            item.trigger = "from"
            item.condition = "is"
            item.value = "BOB@example.co"

        condition = self.cx_message_filter_rule_test_1.condition_ids[-1]
        self.assertTrue(
            condition.condition_other("Bob Robin <bob@example.co>"),
            msg="Condition must be True",
        )
        self.assertTrue(
            condition.condition_other("Bob Robin <BOB@EXAMPLE.co>"),
            msg="Condition must be True",
        )
        self.assertFalse(
            condition.condition_other("Mr Bob <mr.bob@example.co>"),
            msg="Condition must be False",
        )
        self.assertFalse(
            condition.condition_other("Super Bob <superbob@emample.com>"),
            msg="Condition must be False",
        )

        with Form(self.cx_message_filter_test_1) as form, form.rule_ids.edit(
            0
        ) as rule, rule.condition_ids.new() as item:
            item.trigger = "from"
            item.condition = "not"
            item.value = "bob@example.co"

        condition = self.cx_message_filter_rule_test_1.condition_ids[-1]
        self.assertFalse(
            condition.condition_other("Bob Robin <bob@example.co>"),
            msg="Condition must be False",
        )
        self.assertFalse(
            condition.condition_other("Bob Robin <BOB@EXAMPLE.co>"),
            msg="Condition must be False",
        )
        self.assertTrue(
            condition.condition_other("Mr Robin <mr.bob@example.co>"),
            msg="Condition must be True",
        )
        self.assertTrue(
            condition.condition_other("Super Robin <superbob@emample.com>"),
            msg="Condition must be True",
        )
        self.assertTrue(
            condition.condition_other("Example User <example@exmpl.com>"),
            msg="Condition must be True",
        )

        with Form(self.cx_message_filter_test_1) as form, form.rule_ids.edit(
            0
        ) as rule, rule.condition_ids.new() as item:
            item.trigger = "from"
            item.condition = "like"
            item.value = "Bob Robin"

        condition = self.cx_message_filter_rule_test_1.condition_ids[-1]

        self.assertTrue(
            condition.condition_other("Bob Robin <bob@example.co>"),
            msg="Condition must be True",
        )
        self.assertFalse(
            condition.condition_other("Mr Robin <mr.bob@example.co>"),
            msg="Condition must be False",
        )

        with Form(self.cx_message_filter_test_1) as form, form.rule_ids.edit(
            0
        ) as rule, rule.condition_ids.new() as item:
            item.trigger = "to"
            item.condition = "is"
            item.value = "BOB@EX.com"

        condition = self.cx_message_filter_rule_test_1.condition_ids[-1]
        self.assertTrue(
            condition.condition_other("bob@ex.com"), msg="Condition must be True"
        )
        self.assertFalse(
            condition.condition_other("bob@ex.com,bob1@ex.com"),
            msg="Condition must be False",
        )
        self.assertTrue(
            condition.condition_other("BOB@EX.COM"), msg="Condition must be True"
        )

    def test_condition_for_message_spam_filter(self):
        self.mail_message_test_1.mark_spam()
        self.assertFalse(
            self.mail_message_test_1.active, msg="Message active must be True"
        )
        self.assertTrue(
            self.mail_message_test_1.message_filter_id,
            msg="Message must be have filter",
        )
        self.assertEqual(
            self.mail_message_test_1.message_filter_id.id,
            self.cx_message_filter_spam_test_1.id,
            msg="Message filter must be spam filter",
        )

        filter_rule = self.cx_message_filter_spam_test_1.rule_ids
        self.assertEqual(
            len(filter_rule), 1, msg="Count filter rule must be equal to 1"
        )
        rule_id = filter_rule[0]
        self.assertEqual(
            rule_id.message_id,
            self.mail_message_test_1.id,
            msg="Messages ids must be the same",
        )
        self.assertEqual(len(rule_id), 1, msg="Rules count must be equal to 1")
        condition = rule_id.condition_ids[0]
        self.assertEqual(
            condition.trigger, "from", msg="Condition trigger must be equal to 'from'"
        )
        self.assertFalse(
            condition.partner_ids, msg="Condition must don't contain partners"
        )
        self.assertEqual(
            condition.value,
            self.res_partner_bob.email,
            msg="Condition value must be the same with bob's email",
        )
        self.assertEqual(
            condition.condition, "is", msg="Condition must be equal to 'is'"
        )

    def test_spam_filter_set_message_by_condition(self):
        spam_filter = self.cx_message_filter_spam_test_1
        self.mail_message_test_1.mark_spam()

        self.assertEqual(
            self.mail_message_test_1.message_filter_id.id,
            spam_filter.id,
            msg="Message filter must be equal to spam filter",
        )
        with Form(
            spam_filter
        ) as form, form.rule_ids.new() as rule, rule.condition_ids.new() as item:
            item.trigger = "from"
            item.condition = "is"
            item.value = self.res_partner_bob.email
        spam_filter.active = False

        self.mail_message_test_1.unmark_spam()
        spam_filter.write({"active": True})
        self.mail_message_test_1.mark_spam()
        self.assertEqual(
            self.mail_message_test_1.message_filter_id.id,
            spam_filter.id,
            msg="Message filter must be equal to spam filter",
        )

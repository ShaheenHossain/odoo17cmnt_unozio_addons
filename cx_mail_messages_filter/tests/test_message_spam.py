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

from datetime import datetime, timedelta

from odoo.tests import Form

from .common import MailMessagesFilterCommon


class TestMessageSpam(MailMessagesFilterCommon):
    def setUp(self):
        super().setUp()
        mail_message_model = self.env["mail.message"]

        self.mail_message_test_1 = mail_message_model.create(
            {
                "subject": "To Odoo User",
                "body": "Test no html message",
                "email_from": self.res_partner_bob.email,
                "author_id": self.res_partner_bob.id,
            }
        )

        form = Form(self.env["cx.message.filter"])
        form.name = "Test Spam Filter"
        form.action = "x"
        self.cx_message_filter = form.save()

        self.mail_message_test_2 = mail_message_model.create(
            {
                "subject": "To Odoo User",
                "body": "Test no html message",
                "email_from": self.res_partner_max.email,
                "author_id": self.res_partner_max.id,
            }
        )

        self.mail_message_test_3 = mail_message_model.create(
            {
                "subject": "To Odoo User",
                "body": "Test no html message",
                "email_from": self.res_partner_oleg.email,
                "author_id": self.res_partner_oleg.id,
            }
        )

        self.mail_message_test_4 = mail_message_model.create(
            {
                "subject": "To Odoo User",
                "body": "Test no html message",
                "email_from": self.res_partner_mark.email,
                "author_id": self.res_partner_mark.id,
            }
        )

    def test_compute_count_spam_days(self):
        now_datetime = datetime.now()
        old_datetime = now_datetime - timedelta(days=3)
        self.mail_message_test_1.write({"spam_date": old_datetime})
        self.assertEqual(
            self.mail_message_test_1.spam_days,
            3,
            msg="Spam days count must be equal to 3",
        )

    def test_get_or_create_spam_filter(self):
        custom_filter = self.cx_message_filter.get_or_create_spam_filter()
        self.assertTrue(
            custom_filter.action == "x", msg="Filter action must be equal to 'x'"
        )
        self.cx_message_filter.write({"active": False})
        custom_filter = self.cx_message_filter.get_or_create_spam_filter()
        self.assertEqual(
            custom_filter.name,
            "Default Spam Filter",
            msg="Filter name must be equal to default spam filter name",
        )
        self.assertTrue(
            custom_filter.action == "x", msg="Filter action name must be equal to 'x'"
        )
        self.assertTrue(custom_filter.active, msg="Filter must be active")

    def test_check_rule_by_message_filter(self):
        cx_message_filter_rule_obj = self.env["cx.message.filter.rule"]

        self.cx_message_filter.write({"active": True})
        result = self.mail_message_test_1.check_rule_by_message_filter(
            filter_id=self.cx_message_filter.id,
        )
        self.assertFalse(result, msg="Result must be False")

        cx_message_filter_rule_obj.create(
            {
                "filter_id": self.cx_message_filter.id,
                "message_id": self.mail_message_test_1.id,
            }
        )
        result = self.mail_message_test_1.check_rule_by_message_filter(
            filter_id=self.cx_message_filter.id,
        )
        self.assertTrue(result, msg="Result must be True")

        result = self.mail_message_test_1.check_rule_by_message_filter(filter_id=0)
        self.assertFalse(result, msg="Result must be False")

    def test_create_rule_for_spam_filter(self):
        filter_id = self.cx_message_filter.id
        rule = self.mail_message_test_1.create_rule_for_spam_filter(filter_id)
        self.assertTrue(rule, msg="Result must be True")
        rule = self.mail_message_test_1.create_rule_for_spam_filter(0)
        self.assertFalse(rule, msg="Result must be False")
        rule = self.mail_message_test_1.create_rule_for_spam_filter(None)
        self.assertFalse(rule, msg="Result must be False")

    def test_create_spam_condition(self):
        cx_message_filter_rule_obj = self.env["cx.message.filter.rule"]
        rule = cx_message_filter_rule_obj.create(
            {
                "filter_id": self.cx_message_filter.id,
                "message_id": self.mail_message_test_1.id,
            }
        )
        status, error_message = rule.create_spam_condition(False)
        self.assertFalse(status, msg="Status must be False")
        self.assertEqual(error_message, "Message is empty!")

        status, error_message = rule.create_spam_condition(self.mail_message_test_1)
        self.assertTrue(status, msg="Status must be True")
        self.assertEqual(error_message, "Ok!")
        self.mail_message_test_1.write({"email_from": ""})
        status, error_message = rule.create_spam_condition(self.mail_message_test_1)
        self.assertFalse(status, msg="Status must be False")
        self.assertEqual(
            error_message,
            "Message ID [%d] email_from is not found!" % self.mail_message_test_1.id,
            msg="Errors messages must be the same",
        )

    def test_mark_spam(self):
        cx_message_filter_rule_obj = self.env["cx.message.filter.rule"]
        self.cx_message_filter.order = 1
        self.mail_message_test_1.mark_spam()
        self.assertFalse(
            self.mail_message_test_1.active, msg="Message active must be False"
        )
        self.assertTrue(
            self.mail_message_test_1.spam_date,
            msg="Message spam date must be not empty",
        )
        self.assertEqual(
            len(self.cx_message_filter.rule_ids.ids),
            1,
            msg="Filter rules count must be equal to 1",
        )
        rule = cx_message_filter_rule_obj.search(
            [("message_id", "=", self.mail_message_test_1.id)]
        )
        self.assertTrue(rule, msg="Filter has rules")
        self.assertEqual(
            len(rule.condition_ids.ids),
            1,
            msg="Rule conditions count must be equal to 1",
        )
        self.assertEqual(
            rule.filter_id.id,
            self.cx_message_filter.id,
            msg="Filters ids must be the same",
        )
        self.assertEqual(
            rule.message_id,
            self.mail_message_test_1.id,
            msg="Messages ids must be the same",
        )
        self.assertTrue(self.res_partner_bob.spammer, msg="Bob must be mark spammer")
        self.assertFalse(self.res_partner_bob.active, msg="Bob must be archived")

    def test_delete_spam(self):
        messages = self.env["mail.message"].search(
            [("body", "=", "Test no html message")]
        )
        self.assertEqual(len(messages), 4, msg="Message count must be equal to 4")
        message_mark_spam = messages.ids
        messages.mark_spam()
        spam_messages = messages.filtered(lambda msg: msg.spam_date)
        self.assertEqual(
            len(spam_messages), 4, msg="Message mark spam count must be equal to 4"
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "cx_mail_messages_filter.delete_spam_after", 0
        )
        spam_messages._delete_spam()
        messages = (
            self.env["mail.message"]
            .with_context(active_test=False)
            .search([("body", "=", "Test no html message")])
        )
        self.assertListEqual(
            messages.ids, message_mark_spam, msg="List must be the same"
        )
        date_for_delete = datetime.now() - timedelta(days=2)
        self.env["ir.config_parameter"].sudo().set_param(
            "cx_mail_messages_filter.delete_spam_after", 1
        )
        messages.write({"spam_date": date_for_delete})
        messages._delete_spam()
        messages = (
            self.env["mail.message"]
            .with_context(active_test=False)
            .search([("body", "=", "Test no html message")])
        )
        self.assertFalse(messages, msg="Recordset must be empty")

    def test_unmark_spam(self):
        cx_message_filter_rule_obj = self.env["cx.message.filter.rule"]
        self.mail_message_test_1.unlink_pro()
        self.assertTrue(
            self.mail_message_test_1.delete_date, msg="Delete date must be set"
        )
        self.assertFalse(self.mail_message_test_1.active, msg="Message must be active")
        self.assertTrue(
            self.mail_message_test_1.delete_uid, msg="Delete UID must be set"
        )
        self.mail_message_test_1.mark_spam()
        rule = cx_message_filter_rule_obj.search(
            [("message_id", "=", self.mail_message_test_1.id)]
        )
        self.assertTrue(rule, msg="Filter must be has rules")
        self.assertFalse(
            self.mail_message_test_1.active, msg="Message must be deactivate"
        )
        self.assertTrue(self.mail_message_test_1.spam_date, msg="Spam date must be set")
        self.assertTrue(
            self.mail_message_test_1.author_id.spammer,
            msg="Messages author must be mark spammer",
        )
        self.assertFalse(
            self.mail_message_test_1.author_id.active,
            msg="Messages author must be archived",
        )
        self.mail_message_test_1.unmark_spam()
        self.assertFalse(
            self.mail_message_test_1.spam_date, msg="Spam date must not be set"
        )
        self.assertTrue(self.mail_message_test_1.active, msg="Message must be active")
        self.assertTrue(
            self.mail_message_test_1.author_id.active,
            msg="Messages author must be active",
        )
        self.assertFalse(
            self.mail_message_test_1.author_id.spammer,
            msg="Messages author must not be mark spammer",
        )
        rule = cx_message_filter_rule_obj.search(
            [("message_id", "=", self.mail_message_test_1.id)]
        )
        self.assertFalse(rule, msg="Filter must not be has rules")

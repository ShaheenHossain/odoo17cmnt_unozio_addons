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


class TestMessageFilter(MailMessagesFilterCommon):
    def setUp(self):
        super().setUp()

        form = Form(self.env["cx.message.filter"])
        form.name = "Test Filter #1"
        form.action = "m"
        form.destination_model_id = self.ir_model_res_partner
        self.filter = form.save()

        self.msg_dict = {
            "message_type": "email",
            "message_id": "",
            "subject": "test message_new()",
            "from": "Vova Test <test1@example.com>",
            "to": "Administrator <bob@example.com>",
            "cc": "",
            "email_from": "Vova Test <test1@example.com>",
            "date": "2021-08-04 15:08:08",
            "body": '<div dir="ltr"><br></div>\n',
            "attachments": [],
            "author_id": 75,
        }

    def test_condition_recipient(self):
        with Form(
            self.filter
        ) as form, form.rule_ids.new() as rule, rule.condition_ids.new() as item:
            item.trigger = "recipients"
            item.partner_ids.add(self.res_partner_bob)

        condition_recipient = self.filter.rule_ids[0].condition_ids[0]

        result = condition_recipient.condition_recipients(
            ["bob@example.com", "test1@example.com"]
        )
        self.assertTrue(result, msg="Condition result must be True")

        result = condition_recipient.condition_recipients(["test1@example.com"])
        self.assertFalse(result, msg="Condition result must be False")

        condition_recipient.write({"condition": "not_like"})

        result = condition_recipient.condition_recipients(
            ["bob@example.com", "test1@example.com"]
        )
        self.assertFalse(result, msg="Condition result must be False")

        result = condition_recipient.condition_recipients(["test1@example.com"])
        self.assertTrue(result, msg="Condition result must be True")

    def test_condition_author(self):
        with Form(
            self.filter
        ) as form, form.rule_ids.new() as rule, rule.condition_ids.new() as item:
            item.trigger = "author"
            item.partner_ids.add(self.res_partner_bob)
        condition_author = self.filter.rule_ids[0].condition_ids[0]
        result = condition_author.condition_author(self.res_partner_bob.id)
        self.assertTrue(result, msg="Condition result must be True")

        result = condition_author.condition_author(1)
        self.assertFalse(result, msg="Condition result must be False")

        condition_author.write({"condition": "not_like"})

        result = condition_author.condition_author(self.res_partner_bob.id)
        self.assertFalse(result, msg="Condition result must be False")

        result = condition_author.condition_author(1)
        self.assertTrue(result, msg="Condition result must be True")

    def test_condition_other(self):
        with Form(
            self.filter
        ) as form, form.rule_ids.new() as rule, rule.condition_ids.new() as item:
            item.trigger = "subject"
            item.condition = "like"
            item.value = "test"
        condition_text = self.filter.rule_ids[0].condition_ids[0]

        result = condition_text.condition_other("test")
        self.assertTrue(result, msg="Condition result must be True")

        result = condition_text.condition_other("tes1t")
        self.assertFalse(result, msg="Condition result must be False")

        condition_text.write({"condition": "not_like"})

        result = condition_text.condition_other("test")
        self.assertFalse(result, msg="Condition result must be False")

        result = condition_text.condition_other("tes1t")
        self.assertTrue(result, msg="Condition result must be True")

    def test_check_filter_conditions_valid(self):
        with Form(self.filter) as form, form.rule_ids.new() as rule:
            with rule.condition_ids.new() as item:
                item.trigger = "recipients"
                item.condition = "like"
                item.partner_ids.add(self.res_partner_bob)
            with rule.condition_ids.new() as item:
                item.trigger = "author"
                item.condition = "like"
                item.partner_ids.add(self.res_partner_bob)
            with rule.condition_ids.new() as item:
                item.trigger = "subject"
                item.condition = "like"
                item.value = "test"
        self.msg_dict.update(author_id=self.res_partner_bob.id)
        result = self.filter.rule_ids.check_conditions(self.msg_dict)
        self.assertTrue(result, msg="Condition result must be True")

    def test_check_filter_conditions_invalid(self):
        with Form(self.filter) as form, form.rule_ids.new() as rule:
            with rule.condition_ids.new() as item:
                item.trigger = "recipients"
                item.condition = "like"
                item.partner_ids.add(self.res_partner_bob)
            with rule.condition_ids.new() as item:
                item.trigger = "author"
                item.condition = "like"
                item.partner_ids.add(self.res_partner_bob)
            with rule.condition_ids.new() as item:
                item.trigger = "subject"
                item.condition = "like"
                item.value = "test1"
        result = self.filter.rule_ids[0].check_conditions(self.msg_dict)
        self.assertFalse(result, msg="Condition result must be False")

    def test_message_new_empty_filter(self):
        msg_dict = {
            **self.msg_dict,
            "from": "Test1 User1 <demo7@exmaple.com>",
            "to": "demo5@example.com, "
            "Test User <test1@example.com>, "
            "demo6@example.com",
            "email_from": "Test1 User1 <demo7@exmaple.com>",
            "body": '<div dir="ltr"><span>DATA Text</span><br></div>',
        }
        self.filter.unlink()
        model_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("cx_mail_messages_filter.fallback_model_id", False)
        )
        if not model_id:
            self.assertFalse(model_id, msg="Model id must be empty")
        self.env["ir.config_parameter"].sudo().set_param(
            "cx_mail_messages_filter.fallback_model_id",
            self.ref("base.model_res_partner"),
        )
        result = self.env["cx.message.filter"].message_new(msg_dict, custom_values=None)
        model_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("cx_mail_messages_filter.fallback_model_id", False)
        )
        model_config_name = self.env["ir.model"].browse(model_id)._name
        model_valid_name = self.env["ir.model"].browse(result.id)._name
        self.assertEqual(
            model_config_name, model_valid_name, msg="Models must be the same"
        )

    def test_message_new_action_keep_here(self):
        msg_dict = {
            **self.msg_dict,
            "from": "Test1 User1 <demo7@exmaple.com>",
            "to": "demo5@example.com, "
            "Test User <test1@example.com>, "
            "demo6@example.com",
            "email_from": "Test1 User1 <demo7@exmaple.com>",
            "body": '<div dir="ltr"><span>DATA Text</span><br></div>',
            "author_id": 1,
        }
        result = self.env["cx.message.filter"].message_new(msg_dict, custom_values=None)
        self.assertNotEqual(
            result, self.filter, msg="Result must not equal to filter record"
        )

    def test_message_new_post_to_model(self):
        msg_dict = {
            **self.msg_dict,
            "from": "Test1 User1 <demo7@exmaple.com>",
            "to": "demo5@example.com, "
            "Test User <test1@example.com>, "
            "demo6@example.com",
            "email_from": "Test1 User1 <demo7@exmaple.com>",
            "body": '<div dir="ltr"><span>DATA Text</span><br></div>',
            "author_id": 1,
        }
        result = self.env["cx.message.filter"].message_new(msg_dict, custom_values=None)
        model_config = result
        self.assertEqual(
            model_config._name, "res.partner", msg="Models names must be the same"
        )

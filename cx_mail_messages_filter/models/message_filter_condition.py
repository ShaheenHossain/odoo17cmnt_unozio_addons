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

from email.utils import parseaddr

from odoo import _, api, fields, models
from odoo.tools.mail import email_split

from .states import (
    CONDITION,
    CONDITION_STATE_CONTAINS,
    CONDITION_STATE_EQ,
    FILTER_CONDITION,
)


class CxMessageFilterCondition(models.Model):
    _name = "cx.message.filter.condition"
    _description = "Message filter conditions"

    name = fields.Char(
        string="Condition name",
        compute="_compute_name",
        readonly=False,
        store=True,
    )
    rule_id = fields.Many2one(
        "cx.message.filter.rule", string="Filter", ondelete="cascade"
    )
    trigger = fields.Selection(
        FILTER_CONDITION,
        required=True,
    )
    partner_ids = fields.Many2many("res.partner", string="Partners")
    value = fields.Char(string="Search text (optional)")
    condition = fields.Selection(
        [
            ("is", "is"),
            ("not", "not"),
            ("like", "contains"),
            ("not_like", "doesn't contain"),
        ],
        required=True,
        default="like",
    )

    @api.model
    def _check_valid_condition(self, vals=None):
        """
        Check the input data for the correctness
        of the condition
        :param vals: input data dict (optional)
        :return: None
        :raise model.UserError
        """
        vals = vals or dict()
        trigger = vals.get("trigger", self.trigger)
        condition = vals.get("condition", self.condition)
        if not (trigger and condition):
            return
        valid_trigger = trigger in ["author", "recipients"]
        valid_condition = condition in ["is", "not"]
        if valid_trigger and valid_condition:
            raise models.UserError(_("This action cannot be applied to this field!"))

    @api.onchange("trigger", "condition")
    def _onchange_condition(self):
        """
        Check the input data for the correctness
        of the condition at onchange event
        """
        self._check_valid_condition()

    def _get_trigger_by_condition(self):
        """Get trigger name by condition"""
        for key, value in FILTER_CONDITION:
            if key == self.trigger:
                return value
        return ""

    def _prepare_condition_name(self):
        """Prepare condition name"""
        trigger = self._get_trigger_by_condition()
        condition = CONDITION.get(self.condition)
        contains = (
            f"'{self.value}'"
            if self.value
            else " or ".join(self.partner_ids.mapped("name"))
        )
        return f"{trigger} {condition} {contains}"

    @api.depends(
        "rule_id", "trigger", "condition", "value", "partner_ids", "partner_ids.name"
    )
    def _compute_name(self):
        """Compute name for condition"""
        for rec in self:
            rec.name = rec._prepare_condition_name()

    def condition_recipients(self, recipient_emails):
        """Contains email in partner filter

        :param str recipient_emails: from mail incoming recipient email
        :return bool contains/doesn't contain by conditions
        """
        state = False
        if not recipient_emails:
            return False
        for recipient_email in recipient_emails:
            is_partner = self.partner_ids.filtered(
                lambda p, email_=recipient_email: p.email == email_
            )
            if is_partner:
                state = True
                break
        return state ^ CONDITION_STATE_CONTAINS.get(self.condition)

    def condition_author(self, author_id):
        """Contains author id in partner filter

        :param str author_id: mail author id
        :return bool contains/doesn't contain by conditions
        """
        if not author_id:
            return False
        is_partner = self.partner_ids.filtered(lambda p: p.id == author_id)
        return bool(is_partner) ^ CONDITION_STATE_CONTAINS.get(self.condition)

    def condition_other(self, text):
        """Contains value in text filter

        :param str text: contain/doesn't contain search text in mail field
        :return bool contains/doesn't contain by conditions
        """
        if self.condition not in CONDITION_STATE_EQ.keys():
            return (self.value in text) ^ CONDITION_STATE_CONTAINS.get(self.condition)
        value = self.value
        if self.trigger == "from":
            _, text = parseaddr(text)
        if self.trigger in ["from", "to"]:
            text, value = text.lower(), value.lower()
        return (value == text) ^ CONDITION_STATE_EQ.get(self.condition)

    def check_filter_conditions(self, msg_dict):
        """Check all conditions lines in filters

        :param dict msg_dict: dictionary holding parsed message variables
        :return: bool
        """
        author_id = msg_dict.get("author_id", False)
        recipients = email_split(f"{msg_dict.get('to')} {msg_dict.get('cc')}")
        for rec in self:
            condition_author = rec.trigger == "author" and not rec.condition_author(
                author_id
            )
            condition_recipients = (
                rec.trigger == "recipients" and not rec.condition_recipients(recipients)
            )
            condition_other = rec.trigger not in [
                "recipients",
                "author",
            ] and not rec.condition_other(msg_dict.get(rec.trigger, ""))
            if condition_author or condition_recipients or condition_other:
                return False
        return True

    @api.model
    def get_existing_spam_condition(self, email_from):
        """
        Get filter record by spam condition
        :param email_from: email from
        :return: first active filter records or False
        """
        condition = self.search(
            [
                ("trigger", "=", "from"),
                ("condition", "=", "is"),
                ("value", "=", email_from),
            ]
        )
        if not condition:
            return False
        filter_id = condition.mapped("rule_id.filter_id").filtered(lambda f: f.active)
        return filter_id[0] if filter_id else False

    @api.model
    def create(self, vals):
        # Check filter condition
        self._check_valid_condition(vals)
        return super().create(vals)

    def write(self, vals):
        # Check filter condition
        self._check_valid_condition(vals)
        return super().write(vals)

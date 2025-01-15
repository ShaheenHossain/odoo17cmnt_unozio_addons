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

from odoo import api, fields, models


class CxMessageFilterRules(models.Model):
    _name = "cx.message.filter.rule"
    _order = "id desc"

    name = fields.Char("Condition", compute="_compute_name", readonly=False, store=True)

    filter_id = fields.Many2one(
        "cx.message.filter", string="Filter", ondelete="cascade"
    )
    condition_ids = fields.One2many("cx.message.filter.condition", "rule_id")

    message_id = fields.Integer(string="Related Message")

    def _prepare_rule_name(self):
        """Prepare rule name"""
        self.ensure_one()
        return " AND ".join(self.condition_ids.mapped("name"))

    @api.depends("filter_id", "condition_ids", "condition_ids.name")
    def _compute_name(self):
        """Compute rule name"""
        for rec in self:
            rec.name = rec._prepare_rule_name()

    def check_conditions(self, msg_dict):
        """
        Check all conditions from rule
        return: True/False
        """
        for rec in self:
            if rec.condition_ids.check_filter_conditions(msg_dict):
                return True
        return False

    def _create_new_condition(self, email):
        """Create default condition for email"""
        self.condition_ids.create(
            {
                "rule_id": self.id,
                "trigger": "from",
                "condition": "is",
                "value": email,
            }
        )

    def create_spam_condition(self, mail_message):
        """Creations default condition for spam rule"""
        self.ensure_one()
        if not mail_message:
            return False, "Message is empty!"
        email_from = mail_message.email_from
        if not email_from:
            return False, f"Message ID [{mail_message.id}] email_from is not found!"
        _, email = parseaddr(email_from)
        self._create_new_condition(email)
        return True, "Ok!"

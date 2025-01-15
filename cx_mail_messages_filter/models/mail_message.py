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

import logging
from datetime import timedelta
from email.utils import parseaddr

from odoo import fields, models

_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = "mail.message"

    message_filter_id = fields.Many2one("cx.message.filter", string="Mail Filter")

    spam_date = fields.Datetime("Spam on")
    spam_days = fields.Integer("Span days", compute="_compute_spam_days")

    def _compute_spam_days(self):
        """Compute number of days until deletion"""
        date_now = fields.Datetime.now().date()
        for rec in self:
            rec.spam_days = (date_now - rec.spam_date.date()).days

    def _notify_message_notification_update(self):
        return super(
            MailMessage, self.filtered(lambda msg: msg.active and not msg.spam_date)
        )._notify_message_notification_update()

    def check_rule_by_message_filter(self, filter_id):
        """Check rule contain to the filter"""
        self.ensure_one()
        if not filter_id:
            return False
        msg_filter = self.env["cx.message.filter"].browse(filter_id)
        if not msg_filter.exists():
            return False
        rule_id = msg_filter.rule_ids.filtered(lambda rule: rule.message_id == self.id)
        if rule_id:
            return rule_id[0]
        return False

    def create_rule_for_spam_filter(self, filter_id):
        """Get ot create filter for spam message"""
        self.ensure_one()
        if not filter_id:
            return False
        msg_filter = self.env["cx.message.filter"].browse(filter_id)
        if not msg_filter.exists():
            return False
        rule = self.env["cx.message.filter.rule"].create(
            {"filter_id": msg_filter.id, "message_id": self.id}
        )
        return rule

    def _conversations_archive(self):
        """Archive conversation"""
        # Store Conversation ids
        conversations = self.sudo().filtered(lambda r: r.model == "cetmix.conversation")
        if not conversations:
            return
        (
            conversations_2_archive,
            _,
        ) = self._get_conversation_messages_to_delete_and_archive(
            conversations.mapped("res_id")
        )
        if conversations_2_archive:
            self._action_conversation_record(conversations_2_archive, "write")(
                {"active": False}
            )

    def _check_existsing_condition_by_message(self):
        """
        Check condition by email address.
        If has filter condition by email address
        then update message filter id.
        :return: if has filter: True else False
        """
        self.ensure_one()
        if not self.email_from:
            return False
        _, email = parseaddr(self.email_from)
        filter_id = self.env["cx.message.filter.condition"].get_existing_spam_condition(
            email
        )
        if filter_id:
            self.write({"message_filter_id": filter_id.id})
            return True
        return False

    def mark_spam(self):
        """Mark messages to spam"""
        self = self.filtered(lambda msg: not msg.spam_date)
        if not self:
            return
        trash_msg = self.filtered(lambda msg: msg.delete_date)
        if trash_msg:
            trash_msg.undelete()
        self.write(
            {
                "spam_date": fields.Datetime.now(),
                "active": False,
            }
        )
        # Conversation archive
        self._conversations_archive()

        # Mark read messages
        self.mark_read_multi()

        spam_filter = self.env["cx.message.filter"].get_or_create_spam_filter()
        for rec in self:
            if rec._check_existsing_condition_by_message():
                continue
            if rec.check_rule_by_message_filter(spam_filter.id):
                continue
            rec.write({"message_filter_id": spam_filter.id})
            rule = rec.create_rule_for_spam_filter(spam_filter.id)
            if rec.author_id:
                if not rec.author_id.spammer:
                    rec.author_id.set_partner_spammer_on_off()
            status, error_message = rule.create_spam_condition(rec)
            if not status:
                _logger.warning(error_message)

    def _conversation_unarchive(self):
        """Conversation unarchive"""
        res_ids = [
            message.res_id
            for message in self.sudo()
            if message.model == "cetmix.conversation"
        ]
        self.env["cetmix.conversation"].with_context(
            active_test=False, only_conversation=True
        ).search([("active", "=", False), ("id", "in", res_ids)]).write(
            {"active": True}
        )

    def unmark_spam(self):
        """Unmark spam messages"""
        self = self.filtered(lambda msg: msg.spam_date)
        if not self:
            return
        cx_message_filter_rule_obj = self.env["cx.message.filter.rule"]
        self.write(
            {
                "spam_date": False,
                "message_filter_id": False,
            }
        )

        # Unarchive conversation
        self._conversation_unarchive()
        for rec in self:
            if not rec.active or rec.delete_date:
                rec.active = True
            rules = cx_message_filter_rule_obj.search([("message_id", "=", rec.id)])
            rules.unlink()
            if rec.author_id:
                if rec.author_id.spammer:
                    rec.author_id.set_partner_spammer_on_off(state=False)

    def _delete_spam(self):
        """Delete all spam messages by cron"""
        days = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("cx_mail_messages_filter.delete_spam_after", 0)
        )
        if days > 0:
            datetime_from = fields.Datetime.now() - timedelta(days=days)
            spam_messages = self.env["mail.message"].search(
                [
                    ("spam_date", "!=", False),
                    ("spam_date", "<=", datetime_from),
                    ("active", "=", False),
                ]
            )
            spam_messages.unlink()

    # -- Unlink
    def unlink_pro(self):
        """Unlink spam message"""
        if self._context.get("spam_unlink", False):
            return super().unlink_pro()
        spam_msg = self.filtered(lambda msg: msg.spam_date)
        if spam_msg:
            spam_msg.with_context(spam_unlink=True).unlink_pro()
        return super().unlink_pro()

    def archive(self):
        """Don't archive spam messages"""
        return super(
            MailMessage, self.filtered(lambda msg: not msg.spam_date)
        ).archive()

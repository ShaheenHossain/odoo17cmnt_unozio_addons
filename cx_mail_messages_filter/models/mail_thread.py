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

from odoo import api, fields, models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """Checking message spam filter"""
        filter_id = msg_dict.get("message_filter_id")
        if self._context.get("alias_spam") and filter_id:
            filter_ = self.env["cx.message.filter"].browse(filter_id)
            if filter_:
                return filter_
        return super().message_new(msg_dict, custom_values)

    @api.model
    def check_alias_has_check_spam(self, routes):
        """
        Check Alias has check spam state
        :param routes: list message route
        :return: bool
        """
        for route in routes:
            alias_id = route[4]
            if not alias_id:
                continue
            if alias_id.check_spam:
                return True
        return False

    @api.model
    def _message_route_process(self, message, message_dict, routes):
        if not routes:
            return super()._message_route_process(message, message_dict, routes)
        # Message mark spam
        spam_filters = self.env["cx.message.filter"].search(
            [
                ("active", "=", True),
                ("action", "=", "x"),
            ],
        )
        record_filter, _ = spam_filters.get_message_filter(message_dict)
        if record_filter and self.check_alias_has_check_spam(routes):
            message_dict.update(
                {
                    "active": False,
                    "spam_date": fields.Datetime.now(),
                    "message_filter_id": record_filter.id,
                }
            )
            self = self.with_context(alias_spam=True)
        return super()._message_route_process(message, message_dict, routes)

    def _get_message_create_valid_field_names(self):
        result: set = super()._get_message_create_valid_field_names()
        result.update({"message_filter_id", "spam_date", "active"})
        return result

    def message_post(self, *args, **kwargs):
        """
        Return empty record if 'record_ignore` context exists
        Set comment subtype for message if message filter record id is set
        """
        if self._context.get("record_ignore"):
            return self.env["mail.message"]
        if kwargs.get("message_filter_id"):
            kwargs.update(subtype_xmlid="mail.mt_comment")
        return super().message_post(*args, **kwargs)

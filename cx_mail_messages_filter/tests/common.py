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

from odoo.tests import TransactionCase


class MailMessagesFilterCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.res_partner_bob = cls.env.ref("cx_mail_messages_filter.res_partner_bob")
        cls.res_partner_max = cls.env.ref("cx_mail_messages_filter.res_partner_max")
        cls.res_partner_oleg = cls.env.ref("cx_mail_messages_filter.res_partner_oleg")
        cls.res_partner_mark = cls.env.ref("cx_mail_messages_filter.res_partner_mark")

        cls.ir_model_res_partner = cls.env.ref("base.model_res_partner")

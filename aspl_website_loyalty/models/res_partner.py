# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import fields, models, api
from odoo.http import request


class ResPartner(models.Model):
    _inherit = 'res.partner'

    earned_loyalty_ids = fields.One2many('website.earn.loyalty', 'partner_id', string="Earned Loyalty")
    redeem_loyalty_ids = fields.One2many('website.redeem.loyalty', 'partner_id', string="Redeem Loyalty")
    remaining_points = fields.Integer(string="Available Points",  compute='compute_total_earned', store=True)

    @api.depends('earned_loyalty_ids', 'redeem_loyalty_ids')
    def compute_total_earned(self):
        for each in self:
            total_earned = sum(each.earned_loyalty_ids.mapped("points"))
            total_redeem = sum(each.redeem_loyalty_ids.mapped("points"))
            each.remaining_points = total_earned - total_redeem

    def referral_partner(self, email):
        partner_record = self.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        if partner_record:
            sale_order_id = request.session.get('sale_last_order_id')
            sale_order = self.env['sale.order'].browse(sale_order_id)
            sale_order.sudo().write({'partner_id_no': partner_record.id})
            return partner_record

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

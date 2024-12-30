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


class WebsiteEarnLoyalty(models.Model):
    _name = 'website.earn.loyalty'
    _description = 'Reward Points'

    name = fields.Char('Name')
    order_no = fields.Char('Order/Ref')
    order_date = fields.Datetime('Date')
    points = fields.Float('Points')
    partner_id = fields.Many2one('res.partner', 'Customer')
    referral_partner_id = fields.Many2one('res.partner', 'Referred By')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code(
                'website.earn.loyalty') or 'New'
        result = super(WebsiteEarnLoyalty, self).create(vals)
        return result


class WebsiteRedeemLoyalty(models.Model):
    _name = 'website.redeem.loyalty'
    _description = 'Redeem Points for Pos Order'

    name = fields.Char('Name')
    order_no = fields.Char('Order/Ref')
    order_date = fields.Datetime('Date')
    points = fields.Integer('Points')
    points_amount = fields.Integer('Points Amount')
    partner_id = fields.Many2one('res.partner', 'Customer')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code(
                'website.redeem.loyalty') or 'New'
        result = super(WebsiteRedeemLoyalty, self).create(vals)
        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

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
from ast import literal_eval

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_loyalty = fields.Boolean('Loyalty', config_parameter='aspl_website_loyalty.enable_loyalty')
    min_order_value = fields.Integer('Minimum Order Value', config_parameter='aspl_website_loyalty.min_order_value')
    point_calculation = fields.Integer(string='Point Calculation',
                                       config_parameter='aspl_website_loyalty.point_calculation')
    exclude_category = fields.Many2many('product.public.category', string='Exclude Category')
    exclude_tax = fields.Boolean("Exclude Tax", config_parameter='aspl_website_loyalty.exclude_tax')
    amount_per_point = fields.Float("Amount Per Point", config_parameter='aspl_website_loyalty.amount_per_point',
                                    help="""Enter Amount to Calculate per point. E.g : If customer has 10 loyalty 
                                        points and you enter here 0.1 ,then customer gets 1 Loyalty Amount""")
    enable_customer_referral = fields.Boolean('Customer Referral',
                                              config_parameter='aspl_website_loyalty.enable_customer_referral')
    referral_event = fields.Selection([
        ('first_purchase', 'First Purchase'),
        ('every_purchase', 'Every Purchase')
    ], string='Refer Event', config_parameter='aspl_website_loyalty.referral_event')
    referral_point_calculation = fields.Integer('Referral Point Calculation',
                                                config_parameter='aspl_website_loyalty.referral_point_calculation')
    reward_product = fields.Many2one('product.product', domain="[('type','=','service')]",
                                     config_parameter='aspl_website_loyalty.reward_product')

    #
    @api.constrains('referral_point_calculation', 'point_calculation', 'min_order_value', 'amount_per_point')
    def _check_referral_point_calculation(self):
        for record in self:
            if record.referral_point_calculation == 0 and record.enable_customer_referral:
                raise ValidationError(_('Enter Referral Points.'))
            if record.point_calculation == 0 and record.enable_loyalty:
                raise ValidationError(_('Enter Points Calculation.'))
            if record.min_order_value == 0 and record.enable_loyalty:
                raise ValidationError(_('Enter Minimum Order Value.'))
            if record.amount_per_point == 0 and record.enable_loyalty:
                raise ValidationError(_('Enter Amount Per Point Value.'))

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param_obj = self.env['ir.config_parameter'].sudo()
        categories = param_obj.get_param('aspl_website_loyalty.exclude_category')
        res.update(
            exclude_category=[(6, 0, literal_eval(categories))] if categories else False,
        )
        return res

    def set_values(self):
        param_obj = self.env['ir.config_parameter'].sudo()
        param_obj.sudo().set_param('aspl_website_loyalty.exclude_category', self.exclude_category.ids)
        return super(ResConfigSettings, self).set_values()

    @api.model
    def load_loyalty_config_settings(self):
        record = {}

        min_order_value = self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'aspl_website_loyalty.min_order_value')])
        if min_order_value:
            record['min_order_value'] = min_order_value.value

        point_calculation = self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'aspl_website_loyalty.point_calculation')])
        if point_calculation:
            record['point_calculation'] = point_calculation.value

        exclude_tax = self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'aspl_website_loyalty.exclude_tax')])
        if exclude_tax:
            record['exclude_tax'] = exclude_tax.value

        amount_per_point = self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'aspl_website_loyalty.amount_per_point')])
        if amount_per_point:
            record['amount_per_point'] = amount_per_point.value

        enable_customer_referral = self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'aspl_website_loyalty.enable_customer_referral')])
        if enable_customer_referral:
            record['enable_customer_referral'] = enable_customer_referral.value

        referral_event = self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'aspl_website_loyalty.referral_event')])
        if referral_event:
            record['referral_event'] = referral_event.value

        referral_point_calculation = self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'aspl_website_loyalty.referral_point_calculation')])
        if referral_point_calculation:
            record['referral_point_calculation'] = referral_point_calculation.value

        enable_loyalty = self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'aspl_website_loyalty.enable_loyalty')])
        if enable_loyalty:
            record['enable_loyalty'] = enable_loyalty.value

        exclude_category = self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'aspl_website_loyalty.exclude_category')])
        if exclude_category:
            record['exclude_category'] = literal_eval(exclude_category.value)

        return [record]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

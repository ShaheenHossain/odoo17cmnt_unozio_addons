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

import ast
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleInherit(WebsiteSale):

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def shop_payment_confirmation(self, **post):
        res = super(WebsiteSaleInherit, self).shop_payment_confirmation(**post)
        sale_order_id = request.session.get('sale_last_order_id')
        sale_order_rec = request.env['sale.order'].search([('id', '=', sale_order_id)])
        point_calc = float(
            request.env['ir.config_parameter'].sudo().get_param('aspl_website_loyalty.point_calculation'))
        amount_per_point = float(
            request.env['ir.config_parameter'].sudo().get_param('aspl_website_loyalty.amount_per_point'))
        order_total = 0.0
        if request.env['ir.config_parameter'].sudo().get_param('aspl_website_loyalty.exclude_tax'):
            amount = 0.0
            for each in sale_order_rec.order_line:
                amount += each.price_subtotal
            order_total = amount
        else:
            order_total = sale_order_rec.amount_total
        if sale_order_rec.website_id and request.env['ir.config_parameter'].sudo().get_param(
                'aspl_website_loyalty.enable_loyalty') and sale_order_rec.invoice_ids \
                and sale_order_rec.amount_total > int(
            request.env['ir.config_parameter'].sudo().get_param('aspl_website_loyalty.min_order_value')):
            amount = 0.0
            for line in sale_order_rec.order_line:
                if line.product_id.sudo().public_categ_ids:
                    for categ in line.product_id.sudo().public_categ_ids:
                        if categ.id in ast.literal_eval(request.env['ir.config_parameter'].sudo().get_param(
                                'aspl_website_loyalty.exclude_category')):
                            amount += line.sudo().product_id.list_price

            referral_point_calc = float(
                request.env['ir.config_parameter'].sudo().get_param(
                    'aspl_website_loyalty.referral_point_calculation'))
            if request.env['ir.config_parameter'].sudo().get_param(
                    'aspl_website_loyalty.referral_event') == "every_purchase":
                vals = {'order_no': sale_order_rec.name,
                        'points': ((order_total - amount) * referral_point_calc) / 100,
                        'order_date': sale_order_rec.date_order,
                        'partner_id': sale_order_rec.partner_id_no.id,
                        'referral_partner_id': sale_order_rec.partner_id_no.id
                        }
                earned_reward_rec = request.env['website.earn.loyalty'].sudo().create(vals)
            if request.env['ir.config_parameter'].sudo().get_param(
                    'aspl_website_loyalty.referral_event') == "first_purchase":
                sale_orders = request.env['sale.order'].search(
                    [('state', 'not in', ['draft', 'cancel']), ('id', '!=', sale_order_id)])
                first_order = True
                for order in sale_orders:
                    if order.partner_id_no:
                        first_order = False
                if first_order:
                    vals = {'order_no': sale_order_rec.name,
                            'points': ((order_total - amount) * referral_point_calc) / 100,
                            'order_date': sale_order_rec.date_order,
                            'partner_id': sale_order_rec.partner_id_no.id,
                            'referral_partner_id': sale_order_rec.partner_id_no.id
                            }
                    earned_reward_rec = request.env['website.earn.loyalty'].sudo().create(vals)
        return res

    @http.route(['/redeerm/reward'], type='json', auth="public", website=True, sitemap=False)
    def redeem_reward(self, **kwargs):
        sale_order_id = request.session.get('sale_last_order_id')
        sale_order_rec = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
        amount = 0.0
        for line in sale_order_rec.order_line:
            if line.product_id.sudo().public_categ_ids:
                for categ in line.sudo().product_id.public_categ_ids:
                    if categ.id in ast.literal_eval(request.env['ir.config_parameter'].sudo().get_param(
                            'aspl_website_loyalty.exclude_category')):
                        amount += line.sudo().product_id.list_price

        earned_reward_rec = request.env['website.earn.loyalty'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        point_calc = float(
            request.env['ir.config_parameter'].sudo().get_param('aspl_website_loyalty.point_calculation'))
        amount_per_point = float(
            request.env['ir.config_parameter'].sudo().get_param('aspl_website_loyalty.amount_per_point'))
        reward_points = 0.0

        if sale_order_rec and sale_order_rec.partner_id.remaining_points:
            if (sale_order_rec.partner_id.remaining_points * amount_per_point) == (
                    sale_order_rec.amount_total - amount):
                reward_points = sale_order_rec.partner_id.remaining_points * amount_per_point
            if (sale_order_rec.partner_id.remaining_points * amount_per_point) > (sale_order_rec.amount_total - amount):
                reward_points = sale_order_rec.amount_total - amount
            if (sale_order_rec.partner_id.remaining_points * amount_per_point) < (sale_order_rec.amount_total - amount):
                reward_points = sale_order_rec.partner_id.remaining_points * amount_per_point
            points_amount = reward_points  # * amount_per_point
            sale_order_vals = {'reward_amount': points_amount,
                               'order_line': [(0, 0, {'product_id': int(
                                   request.env['ir.config_parameter'].sudo().get_param(
                                       'aspl_website_loyalty.reward_product')),
                                                      'product_uom_qty': 1,
                                                      'price_unit': - points_amount,
                                                      })]}
            sale_order_rec.sudo().write(sale_order_vals)
            values = {'order_no': sale_order_rec.name,
                      'points': points_amount / amount_per_point,
                      'order_date': sale_order_rec.date_order,
                      'partner_id': sale_order_rec.partner_id.id,
                      'points_amount': points_amount,
                      }
            request.env['website.redeem.loyalty'].sudo().create(values)
        return True

    @http.route(['/shop/applied_reward'], type='http', auth="public", website=True)
    def view_applied_reward(self, **post):
        if post.get('type') == 'popover':
            sale_order_id = request.session.get('sale_last_order_id')
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            redeemed_reward = request.env['website.redeem.loyalty'].sudo().search([('order_no', '=', order.name)])
            confirm_order = True
            return request.render("aspl_website_loyalty.view_applied_reward",
                                  {'redeemed_reward': redeemed_reward, 'confirm_order': confirm_order})

    @http.route(['/cancel_reward'], type='json', auth="public", csrf=False, method=['post'], website=True)
    def cancel_gift_card(self, **kw):
        redeem_rec = int(kw.get('redeem_id'))
        sale_order_id = request.session.get('sale_last_order_id')
        sale_order = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
        redeem_reward_rec = request.env['website.redeem.loyalty'].sudo().search([('id', '=', redeem_rec)], limit=1)
        product_id = int(request.env['ir.config_parameter'].sudo().get_param('aspl_website_loyalty.reward_product'))
        record = request.env['sale.order.line'].sudo().search(
            [('order_id', '=', sale_order.id), ('product_id', '=', product_id),
             ('price_subtotal', '=', -redeem_reward_rec.points_amount)], limit=1)
        record.sudo().unlink()
        sale_order.sudo().write({
            'reward_amount': sale_order.reward_amount - redeem_reward_rec.points_amount,
        })
        redeem_reward_rec.unlink()
        return True

    @http.route(['/get_partners'], type='json', auth="public", website=True)
    def get_partners(self):
        referred_partners = []
        partners = request.env['res.partner'].search([])
        for each in partners:
            referred_partners.append({'partner_id': each.id, 'name': each.name})
        return [referred_partners]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

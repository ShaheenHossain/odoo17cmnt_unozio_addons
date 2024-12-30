# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import http, SUPERUSER_ID
from odoo.http import request


class OdooWebsiteGiftWrap(http.Controller):
    	
    @http.route('/shop/cart/giftwrap', type='json', auth="public", methods=['POST'], website=True)
    def wallet(self, notes,product, **post):
        cr, uid, context = request.cr, request.uid, request.context
        
        order = request.website.sale_get_order()

        giftwrap = request.env['giftwrap.configuration'].sudo().browse(product)
      
        order_line_obj = request.env['sale.order.line'].sudo().search([])
        flag = 0
        for i in order_line_obj:
            if i.product_id.id == giftwrap.product_id.id and i.order_id.id == order.id:
                flag = flag + 1

        if flag == 0:
            res = order_line_obj.sudo().create({
                'product_id': giftwrap.product_id.id,
                'name': giftwrap.product_id.name,
                'price_unit': giftwrap.price,
                'order_id': order.id,
                'product_uom':giftwrap.product_id.uom_id.id,
                'name': notes,
            })
          
        return True        
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        

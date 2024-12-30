from odoo import http, _
from odoo.http import request
import json
from odoo.addons.website.controllers.main import Website
from datetime import time, timedelta


class ProductController(http.Controller):

    @http.route(['/shop/product_item'], type='json', csrf=False, auth='public', website=True, methods=['POST'])
    def product_item(self, product_ids=[], **post):
        if product_ids:
            products = request.env['product.template'].sudo().search([('id', 'in', product_ids), ('is_published', '=', True)])
            
            product_dict = [{product.id : product.sales_count } for product in products if product.is_published]
            return {'total_sales_count': product_dict}

    @http.route(['/shop/product_sale'], type='json', csrf=False,auth='public', website=True, methods=['POST'])
    def product_sale(self,productTemplateId, **post):
        products = request.env['product.template'].sudo().browse(productTemplateId)
        count = products.sales_count
        return {'products': products, 'count':count}    
    





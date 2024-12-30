from odoo import http
from odoo.http import request

class WebSaleOrderPage(http.Controller):
    def _prepare_orders_domain(self, partner):
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done'])
        ]

    """('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),"""
    """("order_partner_id","=",[partner.id])"""
    """Usefull fields: order_id, product_id"""
    def _prepare_items_domain(self, partner):
        return [
            ('state', 'in', ['sale', 'done', 'draft', 'sent']),
            ('order_partner_id', 'child_of', [partner.commercial_partner_id.id])
        ]

    @http.route('/reorder', type='http', auth='public', website=True, sitemap=False)
    def reorder_page(self, **kwargs):
        SaleOrder = request.env['sale.order']
#        SaleOrderLine = request.env['sale.order.line']
        partner = request.env.user.partner_id
        domain = self._prepare_orders_domain(partner)
#        items_domain = self._prepare_items_domain(partner)
        orders = SaleOrder.search(domain,limit=20)
        call_for = request.env['ir.module.module'].sudo().search([('name', '=', 'call_for')])
        #items = SaleOrderLine.read_group(items_domain,fields=['product_id','name','x_studio_full_website_category'],groupby='product_id',limit=20)
        #attrs = dir(items)
        values = {
            'call_for': call_for,
            'orders': orders,
        #    'items': items,
        #    'attrs': attrs,
        }
        return request.render("website_quick_reorder.reorder", values)

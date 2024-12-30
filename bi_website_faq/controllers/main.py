# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request


class WebsiteFAQ(http.Controller):

    @http.route(['/web/faq'], type="http", auth="public", website=True, sitemap=True)
    def faq_ans(self, **kw):
        obj = request.env["website.faq"].search([('is_published', '=', True)])
        return request.render("bi_website_faq.web_faq", {"object": obj, })

# -*- coding: utf-8 -*-
# from odoo import http


# class CompanySocialMedia(http.Controller):
#     @http.route('/company_social_media/company_social_media', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/company_social_media/company_social_media/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('company_social_media.listing', {
#             'root': '/company_social_media/company_social_media',
#             'objects': http.request.env['company_social_media.company_social_media'].search([]),
#         })

#     @http.route('/company_social_media/company_social_media/objects/<model("company_social_media.company_social_media"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('company_social_media.object', {
#             'object': obj
#         })


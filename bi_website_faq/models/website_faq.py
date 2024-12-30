# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class WebsiteFAQ(models.Model):
    _name = 'website.faq'
    _description = 'Website FAQ'

    is_published = fields.Boolean(string="Website Published ?")
    name = fields.Text(string="Question")
    answer = fields.Html(string="Answer")

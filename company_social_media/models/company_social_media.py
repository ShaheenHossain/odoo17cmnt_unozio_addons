# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CompanySocialMedia(models.Model):
    _inherit = 'res.company'

    social_media_ids = fields.One2many('social_media','company_id', string="Social Media")

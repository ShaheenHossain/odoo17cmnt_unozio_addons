# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SocialMedia(models.Model):
    _name = 'social_media'
    _description = 'Social Media'

    name = fields.Char(string="Social Media")
    link = fields.Char(string="Link")
    company_id = fields.Many2one('res.company', string="Company", ondelete='cascade')

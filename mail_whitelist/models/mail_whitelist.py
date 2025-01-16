from odoo import fields, models


class MailWhitelist(models.Model):

    _name = 'mail.whitelist'

    mail_server_id = fields.Many2one('ir.mail_server')
    name = fields.Char()
    enabled = fields.Boolean(default=True)

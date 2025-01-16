from odoo import fields, models


class IrMailServer(models.Model):

    _inherit = 'ir.mail_server'

    mail_whitelist_ids = fields.One2many('mail.whitelist', 'mail_server_id')
    enable_whitelist = fields.Boolean(default=True)

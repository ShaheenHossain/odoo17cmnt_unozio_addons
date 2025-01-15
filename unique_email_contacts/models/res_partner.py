import logging

from odoo import models, api, exceptions

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains('email')
    def _constrains_unique_mail(self):
        """
        Check unique e-mail address
        """
        self.ensure_one()
        if self.email:
            result_count = self.env['res.partner'].search_count(
                domain=[
                    ('email', '=', self.email),
                    ('id', '!=', self.id),
                ]
            )
            if result_count != 0:
                raise exceptions.UserError(
                    message="E-mail not unique!"
                )

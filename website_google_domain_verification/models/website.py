# Copyright © 2023 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (support@garazd.biz)
# @author: Iryna Razumovska (support@garazd.biz)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    google_domain_verification_code = fields.Char(
        string='Verification Code',
        help='Google Domain Verification Code that you need to get from a meta-tag.',
    )

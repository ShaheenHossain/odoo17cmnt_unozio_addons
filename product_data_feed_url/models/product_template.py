from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    feed_video_url = fields.Char(string='Video URL')
    feed_mobile_url = fields.Char(string='Mobile URL')
    feed_canonical_url = fields.Char(string='Canonical URL')
    feed_app_url = fields.Char(string='App URL')
    feed_ios_url = fields.Char(
        string='iOS URL',
        help='Custom scheme for iOS app as URL. '
             'For iOS, provide both iPhone & iPad app information if they are different from the general iOS app.',
    )
    feed_android_url = fields.Char(
        string='Android URL',
        help='Custom scheme for Android app as URL. For example: android://electronic',
    )

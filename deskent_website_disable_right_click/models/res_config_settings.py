from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    disable_right_click = fields.Boolean(string="Disable Right Click?")
    show_popup_message = fields.Boolean(string="Show Popup Message?")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('website.disable_right_click', self.disable_right_click)
        self.env['ir.config_parameter'].sudo().set_param('website.show_popup_message', self.show_popup_message)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            disable_right_click=self.env['ir.config_parameter'].sudo().get_param('website.disable_right_click'),
            show_popup_message=self.env['ir.config_parameter'].sudo().get_param('website.show_popup_message'),
        )
        return res

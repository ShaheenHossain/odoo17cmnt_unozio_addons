from odoo import models, fields, api
import json
import urllib
class IframeModel(models.Model):
    _name = 'iframe.model'
    _description = 'Iframe Model'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description', default='Default Name')
    
    dynamic_fields = fields.Html(string='Dynamic Fields', compute='_compute_dynamic_fields', sanitize=False)

    @api.depends("name")
    def _compute_dynamic_fields(self):
        active_ids = self.env.context.get('active_ids', []) or self.env.context.get('active_id')
        model_name = self.env.context.get('active_model')
        ids = ','.join(map(str, active_ids))
        formHTML = f"""
        <div class="app-holder">
            <iframe src='/ulgebra-odoo/home?ids={(ids)}&model={model_name}&appCode=twilioforodoocrm' style='border:0px;'></iframe>
        </div>
        """
        for record in self:
            # Example logic to dynamically generate fields
            record.dynamic_fields = formHTML


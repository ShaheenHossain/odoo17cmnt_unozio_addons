import json

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    update_stock_export = fields.Selection(
        [("manage_warehouse", "By Warehouse"), ("manage_direct", "Not Send Warehouse(Simple Update)")],
        string="Update Stock at Export")
    inventory_location_id = fields.Many2one(comodel_name="eg.inventory.location", string="Inventory Location")
    tax_add_by = fields.Selection([("odoo", "By Odoo"), ("shopify", "By Shopify")], string="Add Tax")

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icpSudo = self.env['ir.config_parameter'].sudo()  # it is given all access
        res.update(
            update_stock_export=icpSudo.get_param('eg_shopify_integration.update_stock_export',
                                                  default="manage_direct"),
            inventory_location_id=icpSudo.get_param('eg_shopify_integration.inventory_location_id',
                                                    default=0) and json.loads(
                icpSudo.get_param('eg_shopify_integration.inventory_location_id', default=0)) or 0,
            tax_add_by=icpSudo.get_param('eg_shopify_integration.tax_add_by', default=None),
        )
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        icpSudo = self.env['ir.config_parameter'].sudo()
        icpSudo.set_param("eg_shopify_integration.update_stock_export", self.update_stock_export)
        icpSudo.set_param("eg_shopify_integration.inventory_location_id",
                          self.inventory_location_id and str(self.inventory_location_id.id) or None)
        icpSudo.set_param("eg_shopify_integration.tax_add_by", self.tax_add_by)
        return res

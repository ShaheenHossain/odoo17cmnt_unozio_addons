from odoo import models


class EgProductTemplate(models.Model):
    _inherit = 'eg.product.template'

    def update_product_export_server(self):
        self.env["product.template"].update_product_at_export()

    def update_product_import_server(self):
        self.env["product.template"].update_product_at_import(server_action=True)

    def update_stock_export_server(self):
        eg_product_tmpl_ids = self.env["eg.product.template"].browse(self._context.get("active_ids"))
        if eg_product_tmpl_ids:
            update_stock_export = eg_product_tmpl_ids[0].instance_id.update_stock_export
            if update_stock_export:
                if update_stock_export == "manage_warehouse":
                    self.env["product.template"].update_product_quantity_export_by_warehouse()
                else:
                    self.env["product.template"].update_stock_at_export_shopify(from_action=True)

    def update_image_export_server(self):
        self.env["product.template"].update_image_at_export_shopify()

    def export_product_shopify_server(self):
        self.env["product.template"].export_product_in_shopify()

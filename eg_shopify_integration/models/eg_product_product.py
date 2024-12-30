from odoo import models


class EgProductProduct(models.Model):
    _inherit = "eg.product.product"

    def update_stock_export(self):
        return
        # self.env["product.template"].update_product_quantity_export()
    # TODO: This method use for update stock at export with location

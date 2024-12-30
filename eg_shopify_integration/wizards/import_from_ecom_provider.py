from odoo import fields, models
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


class ImportFromEComProvider(models.TransientModel):
    _inherit = "import.from.ecom.provider"

    spf_inventory_location_import = fields.Boolean(string="Inventory Location",
                                                   help="Import Inventory location shopify to middle layer")
    spf_product_image = fields.Boolean(string="Product Image", help="Import product image from shopify to middle layer")
    spf_stock_manage = fields.Selection(related="ecom_instance_id.spf_stock_manage", readonly=True, store=True)
    spf_update_quantity_export = fields.Boolean(string="Update Stock",
                                                help="Update stock middle layer to shopify at export")
    spf_update_product_export = fields.Boolean(string="Update Product",
                                               help="Update product middle layer to shopify at export")
    spf_update_product_import = fields.Boolean(string="Update Product",
                                               help="Update product from shopify to odoo and middle layer.")
    spf_update_image_export = fields.Boolean(string="Update Image",
                                             help="Update image from middle layer to shopify at export")
    spf_product_image_sale = fields.Boolean(string="Product Image",
                                            help="Import product image from shopify to middle layer")
    spf_update_required_overwrite = fields.Boolean(string="Update Required Overwrite",
                                                   help="If true so all product is update either which product update required is true is update")
    spf_product = fields.Boolean(string="Product", help="Import Product from shopify to odoo and middle layer")
    spf_product_export = fields.Boolean(string="Product", help="Export product middle layer to shopify")
    spf_stock_from_date = fields.Datetime(string="From Date",
                                          help="Stcok update if any changes in stock after this date")
    spf_import_customer = fields.Boolean(string="Customer", help="Import Customer from shopify to odoo")
    spf_import_sale_order = fields.Boolean(string="Sale Order", help="Import Sale Order from shopify to odoo")
    spf_product_create_default_import = fields.Boolean(string="Default Product Create",
                                                       help="When field is true so when import sale order and product is not in odoo so check true so create product either product is not create and sale order is delete")

    def import_from_ecom_provider(self):
        if not self.ecom_instance_id:
            return {"warning": {"message": (
                "Please select the Instance")}}
        if not self.ecom_instance_id.provider == "eg_shopify":
            return super(ImportFromEComProvider, self).import_from_ecom_provider()
        if self.spf_product:
            self.env["product.template"].import_product_from_shopify(self.ecom_instance_id,
                                                                     product_image=self.spf_product_image)
        if self.spf_product_export:
            self.env["product.template"].export_product_in_shopify(instance_id=self.ecom_instance_id)
        if self.spf_inventory_location_import:
            self.env["product.template"].import_inventory_location(instance_id=self.ecom_instance_id)
        if self.spf_update_product_export:
            self.env["product.template"].update_product_at_export(instance_id=self.ecom_instance_id)
        if self.spf_update_product_import:
            return self.env["product.template"].update_product_at_import(instance_id=self.ecom_instance_id,
                                                                         overwrite_update=self.spf_update_required_overwrite)
        if self.spf_update_image_export:
            self.env["product.template"].update_image_at_export_shopify(instance_id=self.ecom_instance_id)

        if self.spf_update_quantity_export:
            update_stock_export = self.ecom_instance_id.update_stock_export
            if update_stock_export:
                if update_stock_export == "manage_warehouse":
                    action = self.env["product.template"].update_product_quantity_export_by_warehouse(
                        instance_id=self.ecom_instance_id)
                else:
                    action = self.env["product.template"].update_stock_at_export_shopify(
                        spf_from_date=self.spf_stock_from_date,
                        instance_id=self.ecom_instance_id)

        if self.spf_import_customer:
            self.env["res.partner"].import_customer_from_shopify(instance_id=self.ecom_instance_id)
        if self.spf_import_sale_order:
            self.env["sale.order"].import_sale_order_from_shopify(instance_id=self.ecom_instance_id,
                                                                  product_image=self.spf_product_image_sale,
                                                                  product_create=self.spf_product_create_default_import)

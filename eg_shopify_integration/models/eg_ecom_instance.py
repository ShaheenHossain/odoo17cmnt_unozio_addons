from odoo import fields, models, api


class EgEcomInstance(models.Model):
    _inherit = 'eg.ecom.instance'

    spf_stock_manage = fields.Selection([("by_manual", "Manage By Manual"), ("by_shopify", "Manage By Shopify")],
                                        string="Stock Manage")
    update_stock_export = fields.Selection(
        [("manage_warehouse", "By Warehouse"), ("manage_direct", "Not Send Warehouse(Simple Update)")],
        string="Update Stock at Export", readonly=False, default="manage_direct")
    inventory_location_id = fields.Many2one(comodel_name="eg.inventory.location", string="Inventory Location")
    provider = fields.Selection(selection_add=[("eg_shopify", "Shopify")])
    shopify_api_key = fields.Char(string="Api Key")
    shopify_password = fields.Char(string="Password")
    shopify_version = fields.Char(string="Version")
    shopify_shop = fields.Char(string="Shop Name")
    spf_order_name = fields.Selection([("odoo", "By Odoo"), ("shopify", "By Shopify")], string="Sale Order Name")
    tax_add_by = fields.Selection([("odoo", "By Odoo"), ("shopify", "By Shopify")], string="Add Tax")
    spf_last_order_date = fields.Datetime(string="Last Order Date", readonly=True)
    export_stock_date = fields.Datetime(string="Last update stock", readonly=True)

    def test_connection_of_instance(self):
        if self.provider != "eg_shopify":
            return super(EgEcomInstance, self).test_connection_of_instance()
        shop_connection = self.env["product.template"].get_connection_from_shopify(instance_id=self)
        if shop_connection:
            # self.test_connection = True
            self.color = 10
            self.connection_message = "Connection is successful"
            # message = "Connection is successful"
        else:
            # self.test_connection = False
            self.color = 1
            self.connection_message = "Something is wrong !!! not connect to shopify"
            # message = "Something is wrong !!! not connect to shopify"

    @api.model
    def create_sequence_for_shopify_history(self):
        self.env["ir.sequence"].create({"name": "Shopify History Integration",
                                        "code": "eg.ecom.instance",
                                        "prefix": "SH",
                                        "padding": 3,
                                        "number_increment": 1})

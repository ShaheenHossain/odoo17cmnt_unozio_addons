import base64
import json
import logging
from datetime import datetime

import shopify
from requests import request

from odoo import models

_logger = logging.getLogger("=== Import Product Template ===")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def import_product_from_shopify(self, instance_id=None, product_image=None, default_product_id=None):
        status = "no"
        text = ""
        partial = False
        history_id_list = []
        if instance_id:
            shop_connection = self.get_connection_from_shopify(instance_id=instance_id)
            if shop_connection:
                next_page_url = None
                count = 1
                while count > 0:
                    try:
                        if default_product_id:
                            response = shopify.Product.find(default_product_id)
                        else:
                            if next_page_url:
                                response = shopify.Product.find(from_=next_page_url)
                            else:
                                response = shopify.Product.find(limit=250)
                    except Exception as e:
                        return {"warning": {"message": (
                            "{}".format(e))}}

                    if response:
                        product_list = []
                        if default_product_id:
                            product_list.append(response)
                        else:
                            product_list = response
                        for product in product_list:
                            product = product.to_dict()  # convert into dictionary
                            product_template_id = None
                            is_variant = True
                            eg_product_template_id = None
                            eg_product_tmpl_id = self.env["eg.product.template"].search(
                                [("inst_product_tmpl_id", "=", str(product.get("id"))),
                                 ("instance_id", "=", instance_id.id)])
                            if not eg_product_tmpl_id or eg_product_tmpl_id and not eg_product_tmpl_id.odoo_product_tmpl_id:
                                sku = product.get("variants")[0].get("sku")
                                if not sku:
                                    continue
                                product_id = self.env["product.product"].search([("default_code", "=", sku)])
                                product_tmpl_id = None
                                eg_category_id = None
                                if not product_id:
                                    if product.get("product_type"):
                                        category = product.get("product_type").capitalize()
                                        eg_category_id = self.get_mapping_category_at_import_product(category=category,
                                                                                                     instance_id=instance_id)  # start with
                                    option = product.get("options")[0]
                                    attribute_line_list = []
                                    if option.get("name") == "Title" and option.get("values")[0] == "Default Title":
                                        is_variant = False
                                        for product_variant in product.get("variants"):
                                            # Write weight unit
                                            uom_category_id = self.env["uom.category"].search([("name", "=", "Weight")],
                                                                                              limit=1)
                                            uom_id = self.env["uom.uom"].search(
                                                [("name", "in", ["kg", "KG"]),
                                                 ("category_id", "=", uom_category_id.id)], limit=1)
                                            inst_uom_id = self.env["uom.uom"].search(
                                                [("name", "=", product_variant.get("weight_unit")),
                                                 ("category_id", "=", uom_category_id.id)], limit=1)
                                            weight = round(
                                                inst_uom_id._compute_quantity(product_variant.get("weight"), uom_id), 2)

                                            product_tmpl_id = self.create([{"name": product.get("title"),
                                                                            "default_code": product_variant.get("sku"),
                                                                            "type": "product",
                                                                            "standard_price": product_variant.get(
                                                                                "compare_at_price") or 0,
                                                                            "list_price": product_variant.get("price"),
                                                                            "barcode": product_variant.get("barcode"),
                                                                            "categ_id": eg_category_id and eg_category_id.odoo_category_id.id or None,
                                                                            "weight": weight,
                                                                            "qty_available": float(product_variant.get(
                                                                                "old_inventory_quantity")),
                                                                            }]
                                                                          )
                                            eg_product_template_id = self.env["eg.product.template"].create(
                                                {"inst_product_tmpl_id": str(product.get("id")),
                                                 "odoo_product_tmpl_id": product_tmpl_id.id,
                                                 "instance_id": instance_id.id,
                                                 "name": product_tmpl_id.name,
                                                 "price": product_tmpl_id.list_price,
                                                 "default_code": product_tmpl_id.default_code or "",
                                                 "weight": product_tmpl_id.weight,
                                                 "barcode": product_tmpl_id.barcode or "",
                                                 "qty_available": int(product_variant.get("old_inventory_quantity")),
                                                 "update_required": False,
                                                 "description": product.get("body_html"),
                                                 "eg_category_id": eg_category_id and eg_category_id.id or None,
                                                 })
                                    else:
                                        attribute_line_list = self.create_attribute_value_at_import(product=product,
                                                                                                    instance_id=instance_id)

                                    if attribute_line_list:
                                        product_tmpl_id = self.create([{"name": product.get("title"),
                                                                        "type": "product",
                                                                        "categ_id": eg_category_id and eg_category_id.odoo_category_id.id or None,
                                                                        "attribute_line_ids": attribute_line_list[0]}])

                                        eg_product_template_id = self.env["eg.product.template"].create(
                                            {"inst_product_tmpl_id": str(product.get("id")),
                                             "odoo_product_tmpl_id": product_tmpl_id.id,
                                             "instance_id": instance_id.id,
                                             "name": product_tmpl_id.name,
                                             "price": product_tmpl_id.list_price,
                                             "default_code": product_tmpl_id.default_code or "",
                                             "weight": product_tmpl_id.weight,
                                             "barcode": product_tmpl_id.barcode or "",
                                             "qty_available": int(product_tmpl_id.qty_available),
                                             "update_required": False,
                                             "eg_attribute_line_ids": attribute_line_list[1],
                                             "description": product.get("body_html"),
                                             "eg_category_id": eg_category_id and eg_category_id.id or None,
                                             })
                                else:
                                    product_tmpl_id = product_id.product_tmpl_id
                                    create_mapping = self.create_product_variant_at_import(product=product,
                                                                                           instance_id=instance_id,
                                                                                           product_tmpl_id=product_tmpl_id,
                                                                                           check_attribute=True)
                                    if create_mapping:
                                        attribute_line_list = self.create_attribute_value_at_import(product=product,
                                                                                                    instance_id=instance_id,
                                                                                                    product_tmpl_id=product_tmpl_id)
                                        #  new code for v13
                                        if product.get("product_type"):
                                            category = product.get("product_type").capitalize()
                                            eg_category_id = self.get_mapping_category_at_import_product(
                                                category=category,
                                                instance_id=instance_id)

                                        eg_product_template_id = self.env["eg.product.template"].create(
                                            {"inst_product_tmpl_id": str(product.get("id")),
                                             "odoo_product_tmpl_id": product_tmpl_id.id,
                                             "instance_id": instance_id.id,
                                             "name": product_tmpl_id.name,
                                             "price": product_tmpl_id.list_price,
                                             "default_code": product_tmpl_id.default_code or "",
                                             "weight": product_tmpl_id.weight,
                                             "barcode": product_tmpl_id.barcode or "",
                                             "qty_available": int(product_tmpl_id.qty_available),
                                             "update_required": False,
                                             "eg_attribute_line_ids": attribute_line_list[1],
                                             "description": product.get("body_html"),
                                             "eg_category_id": eg_category_id and eg_category_id.id or None
                                             })
                                        self.create_product_variant_at_import(product=product,
                                                                              instance_id=instance_id,
                                                                              product_tmpl_id=product_tmpl_id,
                                                                              eg_product_template_id=eg_product_template_id,
                                                                              check_attribute_create_mapping=True,
                                                                              eg_category_id=eg_category_id)
                                        if product_image:
                                            if not product_tmpl_id.product_variant_ids:
                                                is_variant = False
                                            self.set_product_image_at_import(
                                                eg_product_template_id=eg_product_template_id, product=product,
                                                is_variant=is_variant,
                                                instance_id=instance_id)
                                        status = "yes"
                                        text = "This product was successfully created and mapped"
                                        product_template_id = product_tmpl_id
                                    else:
                                        text = "This odoo product {} is  not same attribute and value for shopify product so it is not mapping".format(
                                            product_id.name)
                                        partial = True
                                        product_template_id = product_tmpl_id
                                        status = "no"
                                        _logger.info(
                                            "This odoo product {} is  not same attribute and value for shopify product so it is not mapping".format(
                                                product_id.name))
                                if not product_id:
                                    if eg_product_template_id:
                                        self.create_product_variant_at_import(product=product,
                                                                              instance_id=instance_id,
                                                                              product_tmpl_id=product_tmpl_id,
                                                                              eg_product_template_id=eg_product_template_id,
                                                                              eg_category_id=eg_category_id)
                                        if product_image:
                                            self.set_product_image_at_import(
                                                eg_product_template_id=eg_product_template_id, product=product,
                                                is_variant=is_variant,
                                                instance_id=instance_id)

                                        status = "yes"
                                        text = "This product was successfully created and mapped"
                                        product_template_id = product_tmpl_id
                                    else:
                                        partial = True
                                        status = "no"
                                        text = "This product is not created and not mapped"
                            else:
                                eg_new_product_tmpl_id = self.create_remaining_product_variant_import(
                                    eg_product_tmpl_id=eg_product_tmpl_id, product=product, instance_id=instance_id)

                                if product_image:
                                    if not eg_product_tmpl_id.odoo_product_tmpl_id.product_variant_ids:
                                        is_variant = False
                                    if eg_new_product_tmpl_id:
                                        self.set_product_image_at_import(
                                            eg_product_template_id=eg_product_tmpl_id, product=product,
                                            is_variant=is_variant,
                                            instance_id=instance_id)
                                text = "This product is already mapped but so update variant"
                                status = "yes"
                                product_template_id = eg_product_tmpl_id.odoo_product_tmpl_id
                            eg_history_id = self.env["eg.sync.history"].create({"error_message": text,
                                                                                "status": status,
                                                                                "process_on": "product",
                                                                                "process": "a",
                                                                                "instance_id": instance_id.id,
                                                                                "product_id": product_template_id and product_template_id.id or None,
                                                                                "child_id": True})
                            history_id_list.append(eg_history_id.id)
                        if default_product_id:
                            break
                        else:
                            next_page_url = response.next_page_url
                            if not next_page_url:
                                break
                    else:
                        text = "Not get response"
                        break
            else:
                text = "Not Connect to store !!!"
        else:
            text = "Not Found Instance !!!"
        if partial:
            status = "partial"
            text = "Some product was created and some product is not create"
        if status == "yes" and not partial:
            text = "All product was successfully created and mapped"
        self.env["eg.sync.history"].create({"error_message": text,
                                            "status": status,
                                            "process_on": "product",
                                            "process": "a",
                                            "instance_id": instance_id and instance_id.id or None,
                                            "parent_id": True,
                                            "eg_history_ids": [(6, 0, history_id_list)]})
        return True

    def get_mapping_category_at_import_product(self, category=None, instance_id=None):
        eg_category_id = None
        if category and instance_id:
            eg_category_id = self.env["eg.product.category"].search(
                [("name", "=", category), ("instance_id", "=", instance_id.id)])
            if not eg_category_id:
                category_id = self.env["product.category"].search([("name", "=", category)], limit=1)
                if not category_id:
                    category_id = self.env["product.category"].create({"name": category})
                if category_id:
                    eg_category_id = self.env["eg.product.category"].create({"odoo_category_id": category_id.id,
                                                                             "instance_id": instance_id.id,
                                                                             })
        return eg_category_id

    def create_product_variant_at_import(self, product=None, instance_id=None, product_tmpl_id=None,
                                         eg_product_template_id=None, check_attribute=None, new_option_list=None,
                                         eg_category_id=None, check_attribute_create_mapping=None):
        same_attribute = True
        for product_variant in product.get("variants"):
            # value_list = []
            eg_product_id = None
            if not check_attribute:
                eg_product_id = self.env["eg.product.product"].search(
                    [("inst_product_id", "=", str(product_variant.get("id"))),
                     ("eg_tmpl_id", "=", eg_product_template_id.id)])
            if not eg_product_id:
                attribute_value_ids = self.env["product.template.attribute.value"]

                for count in range(len(product.get("options"))):
                    attribute_name = product.get("options")[count].get("name")
                    attribute_line_id = None
                    if product_tmpl_id.attribute_line_ids:
                        attribute_line_id = product_tmpl_id.attribute_line_ids.filtered(  # new code for v13
                            lambda l: l.attribute_id.name == attribute_name)
                    if new_option_list:
                        if attribute_name in new_option_list:
                            continue
                    if check_attribute or check_attribute_create_mapping:
                        if product_tmpl_id.attribute_line_ids:
                            attribute_list = product_tmpl_id.attribute_line_ids.mapped("attribute_id.name")
                            if attribute_name not in attribute_list:
                                continue
                    option = "option" + str(count + 1)
                    if product_variant.get(option):
                        condition_list = [("name", "=", product_variant.get(option)),  # new code for v13
                                          ("attribute_id.name", "=", attribute_name)]
                        if attribute_line_id:
                            condition_list.append(("attribute_line_id", "=", attribute_line_id.id))
                        attribute_value_ids += self.env["product.template.attribute.value"].search(condition_list)
                product_id = product_tmpl_id.product_variant_ids.filtered(  # TODO for remove new attribute value
                    lambda l: l.product_template_attribute_value_ids == attribute_value_ids)
                if product_id:
                    if check_attribute:
                        continue
                    uom_category_id = self.env["uom.category"].search([("name", "=", "Weight")],
                                                                      limit=1)
                    uom_id = self.env["uom.uom"].search(
                        [("name", "in", ["kg", "KG"]), ("category_id", "=", uom_category_id.id)], limit=1)
                    inst_uom_id = self.env["uom.uom"].search(
                        [("name", "=", product_variant.get("weight_unit")),
                         ("category_id", "=", uom_category_id.id)], limit=1)
                    weight = round(inst_uom_id._compute_quantity(product_variant.get("weight"), uom_id), 2)
                    product_id.write({"default_code": product_variant.get("sku"),
                                      "standard_price": product_variant.get("compare_at_price") or 0,
                                      "lst_price": product_variant.get("price"),
                                      "barcode": product_variant.get("barcode") or None,
                                      "weight": weight,
                                      })
                    eg_value_ids = self.env["eg.attribute.value"].search(
                        [("odoo_attribute_value_id", "in",
                          product_id.product_template_attribute_value_ids.mapped("product_attribute_value_id.id")),
                         ("instance_id", "=", instance_id.id)])
                    self.env["eg.product.product"].create({"odoo_product_id": product_id.id,
                                                           "instance_id": instance_id.id,
                                                           "inst_product_id": str(product_variant.get("id")),
                                                           "eg_tmpl_id": eg_product_template_id.id,
                                                           "inst_inventory_item_id": str(
                                                               product_variant.get("inventory_item_id")),
                                                           "name": product_id.name,
                                                           "price": product_id.lst_price,
                                                           "default_code": product_id.default_code or "",
                                                           "weight": product_id.weight,
                                                           "barcode": product_id.barcode or "",
                                                           "qty_available": int(product_id.qty_available),
                                                           "update_required": False,
                                                           "eg_value_ids": [(6, 0, eg_value_ids.ids)],
                                                           "eg_category_id": eg_category_id and eg_category_id.id or None,
                                                           })
                else:
                    same_attribute = False

        return same_attribute

    def set_product_image_at_import(self, eg_product_template_id=None, product=None, is_variant=None, instance_id=None):
        eg_product_ids = eg_product_template_id and eg_product_template_id.eg_product_ids or None
        if eg_product_ids:
            if not eg_product_template_id.product_tmpl_image:
                response = None
                try:
                    response = request("GET", url=product.get("image").get("src"))
                except Exception as e:
                    _logger.info("{}".format(e))
                if response and response.status_code == 200:
                    binary_data = base64.b64encode(response.content)
                    if eg_product_template_id:
                        eg_product_template_id.write({"product_tmpl_image": binary_data})
                else:
                    _logger.info("Error is {}".format(response and response.text))
            for image in product.get("images"):
                if image.get("variant_ids") or not is_variant:
                    response_variant = None
                    try:
                        response_variant = request("GET", url=image.get("src"))
                    except Exception as e:
                        _logger.info("{}".format(e))
                    if response_variant and response_variant.status_code == 200:
                        variant_binary_data = base64.b64encode(response_variant.content)
                        new_eg_product_ids = eg_product_ids
                        if is_variant:
                            new_eg_product_ids = eg_product_ids.filtered(
                                lambda l: l.inst_product_id == str(image.get("variant_ids")[0]))
                        new_eg_product_ids[0].write({"product_image": variant_binary_data})
                        new_eg_product_ids[0].write({"inst_product_image_id": str(image.get("id"))})
                    else:
                        _logger.info("Error is {}".format(response_variant and response_variant.text))
                elif not image.get("variant_ids") and image.get("id") != product.get("image").get("id"):
                    response_template = None
                    try:
                        response_template = request("GET", url=image.get("src"))
                    except Exception as e:
                        _logger.info("{}".format(e))
                    if response_template and response_template.status_code == 200:
                        template_binary_data = base64.b64encode(response_template.content)
                        self.env["eg.template.image"].create({"name": str(image.get("id")),
                                                              "template_image": template_binary_data,
                                                              "eg_template_id": eg_product_template_id and eg_product_template_id.id})
        return True

    def export_product_in_middle_layer(self, instance_id=None, product_detail=None, product_image=None):
        product_tmpl_ids = self.browse(self._context.get("active_ids"))
        if product_tmpl_ids:
            product_tmpl_ids = product_tmpl_ids.filtered(lambda l: l.type == "product")
        else:
            product_tmpl_ids = self.search([("type", "=", "product")])
        if product_detail:
            for product_tmpl_id in product_tmpl_ids:
                if product_tmpl_id.product_variant_ids:
                    continue_product = False
                    for product_variant in product_tmpl_id.product_variant_ids:
                        if not product_variant.default_code:
                            continue_product = True
                    if continue_product:
                        continue
                else:
                    if not product_tmpl_id.default_code:
                        continue
                eg_product_tmpl_id = self.env["eg.product.template"].search(
                    [("odoo_product_tmpl_id", "=", product_tmpl_id.id), ("instance_id", "=", instance_id.id)])
                eg_category_id = None
                if not eg_product_tmpl_id:
                    if product_tmpl_id.categ_id:
                        category = product_tmpl_id.categ_id.name
                        eg_category_id = self.get_mapping_category_at_import_product(category=category,
                                                                                     instance_id=instance_id)
                    eg_product_tmpl_id = self.env["eg.product.template"].create(
                        {
                            "odoo_product_tmpl_id": product_tmpl_id.id,
                            "instance_id": instance_id.id,
                            "name": product_tmpl_id.name,
                            "price": product_tmpl_id.list_price,
                            "default_code": product_tmpl_id.default_code or "",
                            "weight": product_tmpl_id.weight,
                            "barcode": product_tmpl_id.barcode or "",
                            "qty_available": int(product_tmpl_id.qty_available),  # Add in Pro Version
                            "update_required": True,
                            "eg_category_id": eg_category_id and eg_category_id.id or None
                        })
                    if product_tmpl_id.attribute_line_ids:
                        attribute_line_list = []
                        for attribute_line_id in product_tmpl_id.attribute_line_ids:
                            eg_attribute_id = self.env["eg.product.attribute"].search(
                                [("odoo_attribute_id", "=", attribute_line_id.attribute_id.id),
                                 ("instance_id", "=", instance_id.id)])
                            value_list = []
                            if not eg_attribute_id:
                                eg_attribute_id = self.env["eg.product.attribute"].create(
                                    {"odoo_attribute_id": attribute_line_id.attribute_id.id,
                                     "instance_id": instance_id.id})
                                for value_id in attribute_line_id.value_ids:
                                    eg_value_id = self.env["eg.attribute.value"].search(
                                        [("inst_attribute_id", "=", eg_attribute_id.id),
                                         ("instance_id", "=", instance_id.id),
                                         ("odoo_attribute_value_id", "=", value_id.id)])
                                    if not eg_value_id:
                                        eg_value_id = self.env["eg.attribute.value"].create(
                                            {"odoo_attribute_value_id": value_id.id,
                                             "inst_attribute_id": eg_attribute_id.id,
                                             "instance_id": instance_id.id,
                                             "odoo_attribute_id": attribute_line_id.attribute_id.id, })
                                    value_list.append(eg_value_id.id)
                                attribute_line_list.append((0, 0, {"eg_product_attribute_id": eg_attribute_id.id,
                                                                   "eg_value_ids": [(6, 0, value_list)]}))
                            else:
                                for value_id in attribute_line_id.value_ids:
                                    eg_value_id = self.env["eg.attribute.value"].search(
                                        [("inst_attribute_id", "=", eg_attribute_id.id),
                                         ("instance_id", "=", instance_id.id),
                                         ("odoo_attribute_value_id", "=", value_id.id)])
                                    if not eg_value_id:
                                        eg_value_id = self.env["eg.attribute.value"].create(
                                            {"odoo_attribute_value_id": value_id.id,
                                             "inst_attribute_id": eg_attribute_id.id,
                                             "instance_id": instance_id.id,
                                             "odoo_attribute_id": attribute_line_id.attribute_id.id, })
                                    value_list.append(eg_value_id.id)
                                attribute_line_list.append((0, 0, {"eg_product_attribute_id": eg_attribute_id.id,
                                                                   "eg_value_ids": [(6, 0, value_list)]}))

                        eg_product_tmpl_id.write({"eg_attribute_line_ids": attribute_line_list})

                    self.export_product_variant_in_middle_layer(instance_id=instance_id,
                                                                eg_product_tmpl_id=eg_product_tmpl_id,
                                                                product_tmpl_id=product_tmpl_id,
                                                                eg_category_id=eg_category_id)
                else:
                    self.export_update_product_in_middle_layer(
                        eg_product_tmpl_id=eg_product_tmpl_id)
        if product_image:
            self.update_product_image_at_export(instance_id=instance_id, product_tmpl_ids=product_tmpl_ids)

    def export_product_variant_in_middle_layer(self, instance_id=None, eg_product_tmpl_id=None, product_tmpl_id=None,
                                               eg_category_id=None):
        if product_tmpl_id.product_variant_ids:
            for product_variant_id in product_tmpl_id.product_variant_ids:
                eg_value_ids = self.env["eg.attribute.value"].search(
                    [("odoo_attribute_value_id", "in",
                      product_variant_id.product_template_attribute_value_ids.mapped("product_attribute_value_id.id")),
                     ("instance_id", "=", instance_id.id)])
                self.env["eg.product.product"].create({"odoo_product_id": product_variant_id.id,
                                                       "instance_id": instance_id.id,
                                                       "eg_tmpl_id": eg_product_tmpl_id.id,
                                                       "name": product_variant_id.name,
                                                       "price": product_variant_id.lst_price,
                                                       "default_code": product_variant_id.default_code or "",
                                                       "weight": product_variant_id.weight,
                                                       "barcode": product_variant_id.barcode or "",
                                                       "qty_available": int(
                                                           product_variant_id.qty_available),
                                                       "eg_value_ids": [(6, 0, eg_value_ids.ids)],
                                                       "update_required": True,
                                                       "eg_category_id": eg_category_id and eg_category_id.id or None
                                                       })

    def export_product_in_shopify(self, instance_id=None):
        status = "no"
        text = ""
        partial = False
        history_id_list = []
        eg_product_tmpl_ids = self.env["eg.product.template"].browse(self._context.get("active_ids"))
        if not eg_product_tmpl_ids:
            eg_product_tmpl_ids = self.env["eg.product.template"].search([("instance_id", "=", instance_id.id)])
        if eg_product_tmpl_ids:
            eg_product_tmpl_ids = eg_product_tmpl_ids.filtered(lambda l: not l.inst_product_tmpl_id)
            for eg_product_tmpl_id in eg_product_tmpl_ids:
                status = "no"
                instance_id = eg_product_tmpl_id.instance_id
                shop_connection = self.get_connection_from_shopify(instance_id=instance_id)
                if shop_connection:
                    vendor = eg_product_tmpl_id.odoo_product_tmpl_id.seller_ids and \
                             eg_product_tmpl_id.odoo_product_tmpl_id.seller_ids[0].display_name or ""

                    product = {"title": eg_product_tmpl_id.name or "",
                               "vendor": vendor,
                               "product_type": eg_product_tmpl_id.eg_category_id and eg_product_tmpl_id.eg_category_id.name or ""
                               }
                    variants = []
                    options = []
                    if eg_product_tmpl_id.eg_attribute_line_ids:
                        for eg_attribute_line_id in eg_product_tmpl_id.eg_attribute_line_ids:
                            options.append({"name": eg_attribute_line_id.eg_product_attribute_id.name,
                                            "values": eg_attribute_line_id.eg_value_ids.mapped("name")})
                        for eg_product_id in eg_product_tmpl_id.eg_product_ids:
                            # Below update code for not change attribute value
                            option = []
                            for eg_attribute_line_id in eg_product_tmpl_id.eg_attribute_line_ids:
                                value_id = eg_product_id.eg_value_ids.filtered(
                                    lambda l: l.inst_attribute_id == eg_attribute_line_id.eg_product_attribute_id)
                                option.append(value_id.name)
                            option_count = len(option)
                            variants.append({"option1": option[0],
                                             "option2": option_count in [2, 3] and option[1] or "",
                                             "option3": option_count == 3 and option[2] or "",
                                             "price": str(eg_product_id.price),
                                             "sku": eg_product_id.default_code or "",
                                             "weight": str(eg_product_id.weight),
                                             "inventory_management": instance_id.spf_stock_manage == "by_shopify" and "shopify" or "",
                                             "weight_unit": "kg",
                                             "inventory_quantity": str(eg_product_id.qty_available),
                                             "barcode": eg_product_id.barcode or ""})

                    else:
                        variants.append({"option1": "Default Title",
                                         "price": str(eg_product_tmpl_id.price),
                                         "sku": eg_product_tmpl_id.default_code or "",
                                         "weight": str(eg_product_tmpl_id.weight),
                                         "weight_unit": "kg",
                                         "inventory_management": instance_id.spf_stock_manage == "by_shopify" and "shopify" or "",
                                         "inventory_quantity": str(eg_product_tmpl_id.qty_available),
                                         "barcode": eg_product_tmpl_id.barcode or ""})
                    product.update({"variants": variants,
                                    "options": options})
                    response = None
                    try:
                        response = shopify.Product.create(product)
                    except Exception as e:
                        text = "This {} product is not export and error is {}".format(eg_product_tmpl_id.name, e)
                        partial = True
                        # error = True
                        _logger.info("This {} product is not export and error is {}".format(eg_product_tmpl_id.name, e))
                    if response and response.id:
                        response = response.to_dict()
                        self.export_product_mapping(response=response,
                                                    eg_product_tmpl_id=eg_product_tmpl_id,
                                                    instance_id=instance_id)
                        status = "yes"
                        text = "This product is successfully export in shopify "
                    elif response:
                        text = "{}".format(response.errors.errors)
                        partial = True

                    eg_history_id = self.env["eg.sync.history"].create({"error_message": text,
                                                                        "status": status,
                                                                        "process_on": "product",
                                                                        "process": "b",
                                                                        "instance_id": instance_id.id,
                                                                        "product_id": eg_product_tmpl_id.odoo_product_tmpl_id.id,
                                                                        "child_id": True})
                    history_id_list.append(eg_history_id.id)
                else:
                    text = "Not Connect to store !!!"
            if partial:
                status = "partial"
                text = "Some product was exported and some product is not exported"
            if status == "yes" and not partial:
                text = "All product was successfully exported in shopify"
            self.env["eg.sync.history"].create({"error_message": text,
                                                "status": status,
                                                "process_on": "product",
                                                "process": "b",
                                                "instance_id": instance_id and instance_id.id or None,
                                                "parent_id": True,
                                                "eg_history_ids": [(6, 0, history_id_list)]})

    def update_product_quantity_export_by_warehouse(self, instance_id=None):
        status = "no"
        text = ""
        partial = False
        history_id_list = []
        eg_product_tmpl_ids = self.env["eg.product.template"].browse(self._context.get("active_ids"))
        if not eg_product_tmpl_ids:
            eg_product_tmpl_ids = self.env["eg.product.template"].search([("instance_id", "=", instance_id.id)])
        if eg_product_tmpl_ids:
            eg_product_tmpl_ids = eg_product_tmpl_ids.filtered(lambda l: l.inst_product_tmpl_id)
        for eg_product_tmpl_id in eg_product_tmpl_ids:
            eg_product_ids = eg_product_tmpl_id.eg_product_ids
            status = "no"
            if eg_product_ids:
                # eg_product_ids = eg_product_ids.filtered(lambda l: l.inst_product_id)
                for eg_product_id in eg_product_ids:
                    instance_id = eg_product_id.instance_id
                    inventory_location_id = instance_id.inventory_location_id
                    inventory_url = "https://{}:{}@{}.myshopify.com/admin/api/{}/{}/{}.json".format(
                        instance_id.shopify_api_key,
                        instance_id.shopify_password,
                        instance_id.shopify_shop,
                        instance_id.shopify_version,
                        #  This method use for update stock at export with location
                        "inventory_levels", "set")
                    header = {'Content-Type': 'application/json'}
                    data = {
                        "location_id": int(inventory_location_id.location_id),
                        "inventory_item_id": int(eg_product_id.inst_inventory_item_id),
                        "available": int(eg_product_id.qty_available)
                    }
                    inventory_response = None
                    error = False
                    try:
                        inventory_response = request("POST", url=inventory_url, headers=header,
                                                     data=json.dumps(data))
                    except Exception as e:
                        text = "This product is not update quantity and error is {}".format(e)
                        partial = True
                        error = True
                        _logger.info("This product {} is not update quantity and error is {}".format(
                            eg_product_id.name, e))
                    if inventory_response and inventory_response.status_code == 200:
                        text = "This product is successfully update stock"
                        status = "yes"
                        _logger.info("This product {} is update quantity".format(eg_product_id.name))
                    elif not error:
                        text = "This product is not update quantity and error is {}".format(inventory_response.text)
                        partial = True
                        _logger.info("This product {} is not update quantity and error is {}".format(
                            eg_product_id.name, inventory_response.text))
                eg_history_id = self.env["eg.sync.history"].create({"error_message": text,
                                                                    "status": status,
                                                                    "process_on": "product",
                                                                    "process": "d",
                                                                    "instance_id": instance_id.id,
                                                                    "product_id": eg_product_tmpl_id.odoo_product_tmpl_id.id,
                                                                    "child_id": True})
                history_id_list.append(eg_history_id.id)
        if partial:
            status = "partial"
            text = "Some product was update stock and some product is not update stock at export"
        if status == "yes" and not partial:
            text = "All product was successfully update stock in shopify at export"
        self.env["eg.sync.history"].create({"error_message": text,
                                            "status": status,
                                            "process_on": "product",
                                            "process": "d",
                                            "instance_id": instance_id and instance_id.id or None,
                                            "parent_id": True,
                                            "eg_history_ids": [(6, 0, history_id_list)]})

    def import_inventory_location(self, instance_id=None):
        status = "no"
        text = ""
        partial = False
        history_id_list = []
        shop_connection = self.get_connection_from_shopify(instance_id=instance_id)
        response = None
        if shop_connection:
            try:
                response = shopify.Location.find(limit=250)
            except Exception as e:
                text = "Not get location and error is {}".format(e)
                _logger.info("Not get location and error is {}".format(e))

            if response:
                for location in response:
                    location = location.to_dict()
                    eg_inventory_location_id = self.env["eg.inventory.location"].search(
                        [("location_id", "=", str(location.get("id"))), ("instance_id", "=", instance_id.id)])
                    if not eg_inventory_location_id:
                        eg_inventory_location_id = self.env["eg.inventory.location"].create(
                            {"name": location.get("name"),
                             "location_id": str(
                                 location.get("id")),
                             "city": location.get("city"),
                             "instance_id": instance_id.id})
                        text = "This inventory location {} is successful create".format(eg_inventory_location_id.name)
                        status = "yes"
                    else:
                        text = "This inventory location {} is already mapped".format(eg_inventory_location_id.name)
                        status = "yes"
                    eg_history_id = self.env["eg.sync.history"].create({"error_message": text,
                                                                        "status": status,
                                                                        "process_on": "product",
                                                                        "process": "a",
                                                                        "instance_id": instance_id.id,
                                                                        "child_id": True})
                    history_id_list.append(eg_history_id.id)
        else:
            text = "Not Connect to store !!!"

        if partial:
            status = "partial"
            text = "Some inventory location is create and some inventory location is not create"
        if status == "yes" and not partial:
            text = "All inventory location was successfully create in middle layer"
        self.env["eg.sync.history"].create({"error_message": text,
                                            "status": status,
                                            "process_on": "product",
                                            "process": "a",
                                            "instance_id": instance_id and instance_id.id or None,
                                            "parent_id": True,
                                            "eg_history_ids": [(6, 0, history_id_list)]})

    def update_product_at_export(self, instance_id=None):
        status = "no"
        text = ""
        partial = False
        history_id_list = []
        eg_product_tmpl_ids = self.env["eg.product.template"].browse(self._context.get("active_ids"))
        if not eg_product_tmpl_ids:
            eg_product_tmpl_ids = self.env["eg.product.template"].search([("instance_id", "=", instance_id.id)])
        if eg_product_tmpl_ids:
            eg_product_tmpl_ids = eg_product_tmpl_ids.filtered(lambda l: l.inst_product_tmpl_id and l.update_required)
            for eg_product_tmpl_id in eg_product_tmpl_ids:
                status = "no"
                instance_id = eg_product_tmpl_id.instance_id
                url = "https://{}:{}@{}.myshopify.com/admin/api/{}/{}/{}.json".format(instance_id.shopify_api_key,
                                                                                      instance_id.shopify_password,
                                                                                      instance_id.shopify_shop,
                                                                                      instance_id.shopify_version,
                                                                                      "products",
                                                                                      eg_product_tmpl_id.inst_product_tmpl_id)
                header = {'Content-Type': 'application/json'}
                product = {"id": eg_product_tmpl_id.inst_product_tmpl_id,
                           "title": eg_product_tmpl_id.name}
                variants = []
                if eg_product_tmpl_id.eg_product_ids:
                    for eg_product_id in eg_product_tmpl_id.eg_product_ids:
                        variants.append({"id": eg_product_id.inst_product_id,
                                         "price": str(eg_product_id.price),
                                         "sku": eg_product_id.default_code or "",
                                         "weight": str(eg_product_id.weight),
                                         "barcode": eg_product_id.barcode or "",
                                         "inventory_quantity": str(eg_product_id.qty_available)})
                product.update({"variants": variants})
                data = {"product": product}
                response = None
                error = False
                try:
                    response = request("PUT", url=url, headers=header, data=json.dumps(data))
                except Exception as e:
                    text = "This {} product is not update at export and error is {}".format(
                        eg_product_tmpl_id.odoo_product_tmpl_id.name, e)
                    partial = True
                    error = True
                    _logger.info("This product is not update at export and error is {}".format(e))
                if response and response.status_code == 200:
                    if response.status_code == 200:
                        eg_product_tmpl_id.write({"update_required": False})
                        for eg_product_id in eg_product_tmpl_id.eg_product_ids:
                            eg_product_id.write({"update_required": False})
                        text = "This product is update at export"
                        status = "yes"
                        _logger.info(
                            "This product {} is update at export".format(eg_product_tmpl_id.odoo_product_tmpl_id.name))
                elif not error:
                    text = "This product is not update at export and error is {}".format(response.text)
                    partial = True
                    _logger.info(
                        "This {} product is not update at export and error is {}".format(
                            eg_product_tmpl_id.odoo_product_tmpl_id.name, response.text))
                eg_history_id = self.env["eg.sync.history"].create({"error_message": text,
                                                                    "status": status,
                                                                    "process_on": "product",
                                                                    "process": "d",
                                                                    "instance_id": instance_id.id,
                                                                    "product_id": eg_product_tmpl_id.odoo_product_tmpl_id.id,
                                                                    "child_id": True})
                history_id_list.append(eg_history_id.id)
            if partial:
                status = "partial"
                text = "Some product was update and some product is not update at export"
            if status == "yes" and not partial:
                text = "All product was successfully update in shopify at export"
            self.env["eg.sync.history"].create({"error_message": text,
                                                "status": status,
                                                "process_on": "product",
                                                "process": "d",
                                                "instance_id": instance_id and instance_id.id or None,
                                                "parent_id": True,
                                                "eg_history_ids": [(6, 0, history_id_list)]})

    def shopify_export_product_stock_by_cron(self):
        instance_ids = self.env["eg.ecom.instance"].search([])
        for instance_id in instance_ids:
            eg_product_tmpl_ids = None
            if instance_id.export_stock_date:
                product_tmpl_ids = list(dict.fromkeys(
                    self.env["stock.move"].search([("date", ">=", instance_id.export_stock_date)]).mapped(
                        "product_id").mapped("product_tmpl_id").ids))
                if product_tmpl_ids:
                    eg_product_tmpl_ids = self.env["eg.product.template"].search(
                        [("instance_id", "=", instance_id.id), ("odoo_product_tmpl_id", "in", product_tmpl_ids)])
                    instance_id.write({"export_stock_date": datetime.now()})
            else:
                eg_product_tmpl_ids = self.env["eg.product.template"].search([("instance_id", "=", instance_id.id)])
                instance_id.write({"export_stock_date": datetime.now()})
            if eg_product_tmpl_ids:
                self.update_stock_at_export_shopify(eg_product_tmpl_ids=eg_product_tmpl_ids)

    def update_stock_at_export_shopify(self, instance_id=None, spf_from_date=None, from_action=None,
                                       eg_product_tmpl_ids=None):
        status = "no"
        text = ""
        partial = False
        history_id_list = []
        if not eg_product_tmpl_ids:
            if not from_action and instance_id and spf_from_date:
                product_tmpl_ids = list(dict.fromkeys(
                    self.env["stock.move"].search([("date", ">=", spf_from_date)]).mapped("product_id").mapped(
                        "product_tmpl_id").ids))
                if product_tmpl_ids:
                    eg_product_tmpl_ids = self.env["eg.product.template"].search(
                        [("instance_id", "=", instance_id.id), ("odoo_product_tmpl_id", "in", product_tmpl_ids)])
            else:
                eg_product_tmpl_ids = self.env["eg.product.template"].browse(self._context.get("active_ids"))
        if eg_product_tmpl_ids:
            eg_product_tmpl_ids = eg_product_tmpl_ids.filtered(lambda l: l.inst_product_tmpl_id)
            for eg_product_tmpl_id in eg_product_tmpl_ids:
                status = "no"
                instance_id = eg_product_tmpl_id.instance_id
                url = "https://{}:{}@{}.myshopify.com/admin/api/{}/{}/{}.json".format(instance_id.shopify_api_key,
                                                                                      instance_id.shopify_password,
                                                                                      instance_id.shopify_shop,
                                                                                      instance_id.shopify_version,
                                                                                      "products",
                                                                                      eg_product_tmpl_id.inst_product_tmpl_id)
                header = {'Content-Type': 'application/json'}
                product = {"id": eg_product_tmpl_id.inst_product_tmpl_id}
                variants = []
                if eg_product_tmpl_id.eg_product_ids:
                    for eg_product_id in eg_product_tmpl_id.eg_product_ids:
                        stock = eg_product_id.odoo_product_id.qty_available - eg_product_id.odoo_product_id.outgoing_qty
                        if stock < 0:
                            stock = 0
                        # variants.append({"id": eg_product_id.inst_product_id,
                        #                  "inventory_quantity": str(int(stock))})
                        instance_id = eg_product_id.instance_id
                        inventory_location_id = instance_id.inventory_location_id
                        inventory_url = "https://{}:{}@{}.myshopify.com/admin/api/{}/{}/{}.json".format(
                            instance_id.shopify_api_key,
                            instance_id.shopify_password,
                            instance_id.shopify_shop,
                            instance_id.shopify_version,
                            #  This method use for update stock at export with location
                            "inventory_levels", "set")
                        header = {'Content-Type': 'application/json'}
                        data = {
                            "location_id": int(inventory_location_id.location_id),
                            "inventory_item_id": int(eg_product_id.inst_inventory_item_id),
                            "available": int(eg_product_id.qty_available)
                        }
                        try:
                            inventory_response = request("POST", url=inventory_url, headers=header,
                                                         data=json.dumps(data))
                        except Exception as e:
                            text = "This product is not update quantity and error is {}".format(e)
                product.update({"variants": variants})
                data = {"product": product}
                response = None
                error = False
                try:
                    response = request("PUT", url=url, headers=header, data=json.dumps(data))
                except Exception as e:
                    text = "This product is not update stock at export and error is {}".format(e)
                    partial = True
                    error = True
                    _logger.info("This {} product is not update stock at export and error is {}".format(
                        eg_product_tmpl_id.odoo_product_tmpl_id.name, e))
                if response and response.status_code == 200:
                    text = "This product is update stock at export"
                    status = "yes"
                    _logger.info(
                        "This product {} is update stock at export".format(
                            eg_product_tmpl_id.odoo_product_tmpl_id.name))
                elif not error:
                    text = "This product is not update stock at export and error is {}".format(response.text)
                    partial = True
                    _logger.info(
                        "This {} product is not update stock at export and error is {}".format(
                            eg_product_tmpl_id.odoo_product_tmpl_id.name, response.text))
                eg_history_id = self.env["eg.sync.history"].create({"error_message": text,
                                                                    "status": status,
                                                                    "process_on": "product",
                                                                    "process": "d",
                                                                    "instance_id": instance_id.id,
                                                                    "product_id": eg_product_tmpl_id.odoo_product_tmpl_id.id,
                                                                    "child_id": True})
                history_id_list.append(eg_history_id.id)
            if partial:
                status = "partial"
                text = "Some product was update stock and some product is not update stock at export"
            if status == "yes" and not partial:
                text = "All product was successfully update stock in shopify at export"
            self.env["eg.sync.history"].create({"error_message": text,
                                                "status": status,
                                                "process_on": "product",
                                                "process": "d",
                                                "instance_id": instance_id and instance_id.id or None,
                                                "parent_id": True,
                                                "eg_history_ids": [(6, 0, history_id_list)]})

    def update_image_at_export_shopify(self, instance_id=None):
        status = "no"
        text = ""
        partial = False
        history_id_list = []
        eg_product_tmpl_ids = self.env["eg.product.template"].browse(self._context.get("active_ids"))
        if not eg_product_tmpl_ids:
            eg_product_tmpl_ids = self.env["eg.product.template"].search([("instance_id", "=", instance_id.id)])
        if eg_product_tmpl_ids:
            eg_product_tmpl_ids = eg_product_tmpl_ids.filtered(lambda l: l.inst_product_tmpl_id)
            for eg_product_tmpl_id in eg_product_tmpl_ids:
                text = ""
                instance_id = eg_product_tmpl_id.instance_id
                url = "https://{}:{}@{}.myshopify.com/admin/api/{}/{}/{}.json".format(instance_id.shopify_api_key,
                                                                                      instance_id.shopify_password,
                                                                                      instance_id.shopify_shop,
                                                                                      instance_id.shopify_version,
                                                                                      "products",
                                                                                      eg_product_tmpl_id.inst_product_tmpl_id)
                header = {'Content-Type': 'application/json'}
                product = {"id": eg_product_tmpl_id.inst_product_tmpl_id
                           }
                images = []
                if eg_product_tmpl_id.eg_product_ids:
                    if eg_product_tmpl_id.product_tmpl_image:
                        images.append({"attachment": str(eg_product_tmpl_id.product_tmpl_image.decode("UTF-8")),
                                       "position": 1,
                                       "product_id": eg_product_tmpl_id.inst_product_tmpl_id,
                                       "variant_ids": []
                                       })
                    for eg_product_id in eg_product_tmpl_id.eg_product_ids:
                        images.append({"attachment": eg_product_id.product_image and str(
                            eg_product_id.product_image.decode("UTF-8")) or "",
                                       "variant_ids": [eg_product_id.inst_product_id]})
                if images:
                    product.update({"images": images})
                    data = {"product": product}
                    response = None
                    try:
                        response = request("PUT", url=url, headers=header, data=json.dumps(data))
                    except Exception as e:
                        text = "This product is not update image at export and error is {}".format(e)
                        partial = True
                        _logger.info("This {} product is not update image at export and error is {}".format(
                            eg_product_tmpl_id.odoo_product_tmpl_id.name, e))
                    if response and response.status_code == 200:
                        text = "This product is update image at export"
                        status = "yes"
                        _logger.info(
                            "This product {} is update image at export".format(
                                eg_product_tmpl_id.odoo_product_tmpl_id.name))
                    elif response:
                        text = "This product is not update image at export and error is {}".format(response.text)
                        partial = True
                        _logger.info(
                            "This {} product is not update image at export and error is {}".format(
                                eg_product_tmpl_id.odoo_product_tmpl_id.name, response.text))
                else:
                    text = "Image is not available in this product"
                    partial = True
                    _logger.info("Image is not available in this product : {}".format(
                        eg_product_tmpl_id.odoo_product_tmpl_id.name))
                eg_history_id = self.env["eg.sync.history"].create({"error_message": text,
                                                                    "status": status,
                                                                    "process_on": "product",
                                                                    "process": "d",
                                                                    "instance_id": instance_id.id,
                                                                    "product_id": eg_product_tmpl_id.odoo_product_tmpl_id.id,
                                                                    "child_id": True})
                history_id_list.append(eg_history_id.id)
            if partial:
                status = "partial"
                text = "Some product was update image and some product is not update image at export"
            if status == "yes" and not partial:
                text = "All product was successfully update image in shopify at export"
            self.env["eg.sync.history"].create({"error_message": text,
                                                "status": status,
                                                "process_on": "product",
                                                "process": "d",
                                                "instance_id": instance_id and instance_id.id or None,
                                                "parent_id": True,
                                                "eg_history_ids": [(6, 0, history_id_list)]})

    def update_product_at_import(self, instance_id=None, server_action=None, overwrite_update=None):
        status = "no"
        text = ""
        partial = False
        history_id_list = []
        eg_product_tmpl_ids = self.env["eg.product.template"].browse(self._context.get("active_ids"))
        if eg_product_tmpl_ids:
            eg_product_tmpl_ids = eg_product_tmpl_ids.filtered(lambda l: not l.update_required)
        else:
            if overwrite_update:
                eg_product_tmpl_ids = self.env["eg.product.template"].search(
                    [("instance_id", "=", instance_id.id), ("inst_product_tmpl_id", "!=", None)])
            else:
                eg_product_tmpl_ids = self.env["eg.product.template"].search(
                    [("instance_id", "=", instance_id.id), ("inst_product_tmpl_id", "!=", None),
                     ("update_required", "=", False)])
        for eg_product_tmpl_id in eg_product_tmpl_ids:
            if eg_product_tmpl_id.inst_product_tmpl_id:
                status = "no"
                if server_action:
                    instance_id = eg_product_tmpl_id.instance_id
                shop_connection = self.get_connection_from_shopify(instance_id=instance_id)
                if shop_connection:

                    response = None
                    try:
                        response = shopify.Product.find(int(
                            eg_product_tmpl_id.inst_product_tmpl_id))  # change method code because import all product
                    except Exception as e:
                        text = "{}".format(e)
                        partial = True

                    if response:
                        product = response.to_dict()
                        if product.get("id") == int(eg_product_tmpl_id.inst_product_tmpl_id):
                            category = product.get("product_type").capitalize()
                            eg_category_id = None
                            if eg_product_tmpl_id.eg_category_id:
                                if not category == eg_product_tmpl_id.eg_category_id.name:
                                    eg_category_id = self.get_mapping_category_at_import_product(category=category,
                                                                                                 instance_id=instance_id)
                                    if eg_category_id:
                                        eg_product_tmpl_id.write({"eg_category_id": eg_category_id.id})
                            if eg_product_tmpl_id.eg_product_ids:
                                for eg_product_id in eg_product_tmpl_id.eg_product_ids:
                                    for product_variant in product.get("variants"):
                                        if product_variant.get("id") == int(eg_product_id.inst_product_id):
                                            uom_category_id = self.env["uom.category"].search([("name", "=", "Weight")],
                                                                                              limit=1)
                                            uom_id = self.env["uom.uom"].search(
                                                [("name", "in", ["kg", "KG"]),
                                                 ("category_id", "=", uom_category_id.id)], limit=1)
                                            inst_uom_id = self.env["uom.uom"].search(
                                                [("name", "=", product_variant.get("weight_unit")),
                                                 ("category_id", "=", uom_category_id.id)], limit=1)
                                            weight = round(
                                                inst_uom_id._compute_quantity(product_variant.get("weight"), uom_id), 2)

                                            eg_product_value = {"name": product.get("title"),
                                                                "price": product_variant.get("price"),
                                                                "default_code": product_variant.get("sku") or "",
                                                                "weight": weight,
                                                                "barcode": product_variant.get(
                                                                    "barcode") or "",
                                                                "qty_available": product_variant.get(
                                                                    "inventory_quantity") or None, }
                                            if eg_category_id:
                                                eg_product_value.update({"eg_category_id": eg_category_id.id})
                                            eg_product_id.write(eg_product_value)
                                            if product_variant.get("title") == "Default Title":
                                                eg_product_tmpl_id.write({"name": product.get("title"),
                                                                          "price": product_variant.get("price"),
                                                                          "default_code": product_variant.get(
                                                                              "sku") or "",
                                                                          "weight": weight,
                                                                          "barcode": product_variant.get(
                                                                              "barcode") or "",
                                                                          "qty_available": product_variant.get(
                                                                              "inventory_quantity") or None,
                                                                          })
                                            _logger.info("This product {} is update at import".format(
                                                eg_product_id.odoo_product_id.name))
                                status = "yes"
                                text = "This product was successfully update"
                        else:
                            text = "Mapping product and response product are not same so don't update product"
                            partial = True
                else:
                    text = "Not Connect to store !!!"
                    partial = True
            else:
                text = "This product have not shopify product id so product was not update "
                partial = True
            eg_history_id = self.env["eg.sync.history"].create({"error_message": text,
                                                                "status": status,
                                                                "process_on": "product",
                                                                "process": "c",
                                                                "instance_id": instance_id.id,
                                                                "product_id": eg_product_tmpl_id.odoo_product_tmpl_id.id,
                                                                "child_id": True})
            history_id_list.append(eg_history_id.id)
        if partial:
            status = "partial"
            text = "Some product was update and some product is not update"
        if status == "yes" and not partial:
            text = "All product was successfully update."
        self.env["eg.sync.history"].create({"error_message": text,
                                            "status": status,
                                            "process_on": "product",
                                            "process": "c",
                                            "instance_id": instance_id and instance_id.id or None,
                                            "parent_id": True,
                                            "eg_history_ids": [(6, 0, history_id_list)]})

    def update_product_image_at_export(self, instance_id=None, product_tmpl_ids=None):
        if instance_id:
            eg_product_tmpl_ids = self.env["eg.product.template"].search(
                [("instance_id", "=", instance_id.id), ("product_tmpl_image", "=", None),
                 ("odoo_product_tmpl_id", "in", product_tmpl_ids.ids)])
            if eg_product_tmpl_ids:
                for eg_product_tmpl_id in eg_product_tmpl_ids:
                    eg_product_tmpl_id.write(
                        {"product_tmpl_image": eg_product_tmpl_id.odoo_product_tmpl_id.image_1920 or None})
                    for eg_product_id in eg_product_tmpl_id.eg_product_ids:
                        for product_id in eg_product_tmpl_id.odoo_product_tmpl_id.product_variant_ids:
                            if eg_product_id.odoo_product_id == product_id:
                                eg_product_id.write({"product_image": product_id.image_1920})
                                break

    def get_connection_from_shopify(self, instance_id=None):
        shop_url = "https://{}:{}@{}.myshopify.com/admin/api/{}".format(instance_id.shopify_api_key,
                                                                        instance_id.shopify_password,
                                                                        instance_id.shopify_shop,
                                                                        instance_id.shopify_version)
        try:
            shopify.ShopifyResource.set_site(shop_url)
            connection = True
        except Exception as e:
            _logger.info("{}".format(e))
            connection = False
        return connection

    def create_remaining_product_variant_import(self, eg_product_tmpl_id=None, product=None, instance_id=None):
        if eg_product_tmpl_id and product:
            option = product.get("options")[0]
            if option.get("name") == "Title" and option.get("values")[0] == "Default Title":
                return True
            variant_mapping = False
            new_option_list = []
            product_tmpl_id = eg_product_tmpl_id.odoo_product_tmpl_id
            for option in product.get("options"):
                value_list = []
                eg_value_list = []
                attribute_id = self.env["product.attribute"].search([("name", "=", option.get("name"))])
                attribute_line_id = None
                eg_product_attribute_id = self.env["eg.product.attribute"].search(
                    [("name", "=", option.get("name")), ("instance_id", "=", instance_id.id)])
                if attribute_id:
                    if not eg_product_attribute_id:
                        eg_product_attribute_id = self.env["eg.product.attribute"].create(
                            {"odoo_attribute_id": attribute_id.id,
                             "instance_id": instance_id.id,
                             "inst_attribute_id": str(option.get("id"))})

                    attribute_line_id = product_tmpl_id.attribute_line_ids.filtered(
                        lambda l: l.attribute_id == attribute_id)

                    if attribute_line_id:
                        for value in option.get("values"):
                            value_id = self.env["product.attribute.value"].search(
                                [("name", "=", value), ("attribute_id", "=", attribute_id.id)])
                            eg_value_id = self.env["eg.attribute.value"].search(
                                [("odoo_attribute_id", "=", attribute_id.id),
                                 ("name", "=", value), ("instance_id", "=", instance_id.id)])
                            if value_id:
                                if not eg_value_id:
                                    eg_value_id = self.env["eg.attribute.value"].create(
                                        {"odoo_attribute_value_id": value_id.id,
                                         "inst_attribute_id": eg_product_attribute_id.id,
                                         "instance_id": instance_id.id,
                                         "odoo_attribute_id": attribute_id.id,
                                         })
                                for attribute_line in product_tmpl_id.attribute_line_ids:
                                    if attribute_line.attribute_id == attribute_id and attribute_line.value_ids and value_id not in attribute_line.value_ids:
                                        value_list.append(value_id.id)
                                        eg_value_list.append(eg_value_id.id)
                            else:
                                value_id = self.env["product.attribute.value"].create({"attribute_id": attribute_id.id,
                                                                                       "name": value})
                                eg_value_id = self.env["eg.attribute.value"].create(
                                    {"odoo_attribute_value_id": value_id.id,
                                     "inst_attribute_id": eg_product_attribute_id.id,
                                     "instance_id": instance_id.id,
                                     "odoo_attribute_id": attribute_id.id,
                                     })
                                value_list.append(value_id.id)
                                eg_value_list.append(eg_value_id.id)
                        if value_list and eg_value_list:
                            attribute_line_id = self.env["product.template.attribute.line"].search(
                                [("product_tmpl_id", "=", product_tmpl_id.id), ("attribute_id", "=", attribute_id.id),
                                 ("value_ids", "!=", None)])
                            eg_attribute_line_id = self.env["eg.product.attribute.line"].search(
                                [("eg_product_tmpl_id", "=", eg_product_tmpl_id.id),
                                 ("eg_product_attribute_id", "=", eg_product_attribute_id.id),
                                 ("eg_value_ids", "!=", None)])
                            if attribute_line_id:
                                for value_id in value_list:
                                    attribute_line_id.write({"value_ids": [(4, value_id, 0)]})  # Start this code
                                product_tmpl_id._create_variant_ids()
                            if eg_attribute_line_id:
                                for eg_value_id in eg_value_list:
                                    eg_attribute_line_id.write({"eg_value_ids": [(4, eg_value_id, 0)]})
                                variant_mapping = True
                if not attribute_id or not attribute_line_id:
                    new_option_list.append(option.get("name"))
            if variant_mapping:
                self.create_product_variant_at_import(instance_id=instance_id, product=product,
                                                      product_tmpl_id=product_tmpl_id,
                                                      eg_product_template_id=eg_product_tmpl_id,
                                                      new_option_list=new_option_list)
                return True
            else:
                return False

    def export_update_product_in_middle_layer(self, eg_product_tmpl_id=None):
        if eg_product_tmpl_id:
            product_tmpl_id = eg_product_tmpl_id.odoo_product_tmpl_id
            eg_product_tmpl_id.write({"name": product_tmpl_id.name,
                                      "price": product_tmpl_id.list_price,
                                      "default_code": product_tmpl_id.default_code or "",
                                      "weight": product_tmpl_id.weight,
                                      "barcode": product_tmpl_id.barcode or "",
                                      "qty_available": int(product_tmpl_id.qty_available),
                                      "update_required": True, })
            for eg_product_id in eg_product_tmpl_id.eg_product_ids:
                product_id = eg_product_id.odoo_product_id
                eg_product_id.write({"name": product_id.name,
                                     "price": product_id.lst_price,
                                     "default_code": product_id.default_code or "",
                                     "weight": product_id.weight,
                                     "barcode": product_id.barcode or "",
                                     "qty_available": int(product_id.qty_available),
                                     "update_required": True, })
            return True

    def create_attribute_value_at_import(self, product=None, instance_id=None,
                                         product_tmpl_id=None):  # new code for v13
        attribute_line_list = []
        eg_attribute_line_list = []
        for option in product.get("options"):
            if option.get("name") == "Title" and option.get("values")[0] == "Default Title":
                continue
            if product_tmpl_id:
                attribute_line_id = product_tmpl_id.attribute_line_ids.filtered(  # new code for v13
                    lambda l: l.attribute_id.name == option.get("name"))
                if not attribute_line_id:
                    continue
            eg_product_attribute_id = self.env["eg.product.attribute"].search(
                [("name", "=", option.get("name")), ("instance_id", "=", instance_id.id)])
            value_list = []
            eg_value_list = []
            if not eg_product_attribute_id:
                product_attribute_id = self.env["product.attribute"].search(
                    [("name", "=", option.get("name"))])
                if not product_attribute_id:
                    product_attribute_id = self.env[
                        "product.attribute"].create({"name": option.get("name")})
                    eg_product_attribute_id = self.env["eg.product.attribute"].create(
                        {"odoo_attribute_id": product_attribute_id.id,
                         "instance_id": instance_id.id,
                         "inst_attribute_id": str(option.get("id"))})
                    for value in option.get("values"):
                        attribute_value_id = self.env["product.attribute.value"].create(
                            {"attribute_id": product_attribute_id.id,
                             "name": value})
                        eg_attribute_value_id = self.env["eg.attribute.value"].create(
                            {"odoo_attribute_value_id": attribute_value_id.id,
                             "inst_attribute_id": eg_product_attribute_id.id,
                             "instance_id": instance_id.id,
                             "odoo_attribute_id": product_attribute_id.id,
                             })
                        value_list.append(attribute_value_id.id)
                        eg_value_list.append(eg_attribute_value_id.id)
                    attribute_line_list.append((0, 0, {"attribute_id": product_attribute_id.id,
                                                       "value_ids": [(6, 0, value_list)]}))
                    eg_attribute_line_list.append((0, 0, {"eg_product_attribute_id": eg_product_attribute_id.id,
                                                          "eg_value_ids": [(6, 0, eg_value_list)]}))

                else:
                    eg_product_attribute_id = self.env["eg.product.attribute"].create(
                        {"odoo_attribute_id": product_attribute_id.id,
                         "instance_id": instance_id.id,
                         "inst_attribute_id": str(option.get("id"))})
                    for value in option.get("values"):
                        attribute_value_id = self.env["product.attribute.value"].search(
                            [("name", "=", value), ("attribute_id", "=", product_attribute_id.id)])
                        if not attribute_value_id:
                            attribute_value_id = self.env["product.attribute.value"].create(
                                {"attribute_id": product_attribute_id.id,
                                 "name": value})

                            eg_attribute_value_id = self.env["eg.attribute.value"].create(
                                {"odoo_attribute_value_id": attribute_value_id.id,
                                 "inst_attribute_id": eg_product_attribute_id.id,
                                 "instance_id": instance_id.id,
                                 "odoo_attribute_id": product_attribute_id.id,
                                 })
                        else:
                            eg_attribute_value_id = self.env["eg.attribute.value"].search(
                                [("odoo_attribute_value_id", "=", attribute_value_id.id),
                                 ("instance_id", "=", instance_id.id),
                                 ("odoo_attribute_id", "=", product_attribute_id.id)])
                            if not eg_attribute_value_id:
                                eg_attribute_value_id = self.env["eg.attribute.value"].create(
                                    {"odoo_attribute_value_id": attribute_value_id.id,
                                     "inst_attribute_id": eg_product_attribute_id.id,
                                     "instance_id": instance_id.id,
                                     "odoo_attribute_id": product_attribute_id.id,
                                     })
                        value_list.append(attribute_value_id.id)
                        eg_value_list.append(eg_attribute_value_id.id)
                    attribute_line_list.append((0, 0, {"attribute_id": product_attribute_id.id,
                                                       "value_ids": [(6, 0, value_list)]}))
                    eg_attribute_line_list.append((0, 0, {"eg_product_attribute_id": eg_product_attribute_id.id,
                                                          "eg_value_ids": [(6, 0, eg_value_list)]}))

            else:
                product_attribute_id = eg_product_attribute_id.odoo_attribute_id
                for value in option.get("values"):
                    eg_attribute_value_id = self.env["eg.attribute.value"].search(
                        [("odoo_attribute_id", "=", product_attribute_id.id),
                         ("name", "=", value), ("instance_id", "=", instance_id.id)])
                    if not eg_attribute_value_id:
                        attribute_value_id = self.env["product.attribute.value"].search(
                            [("name", "=", value), ("attribute_id", "=", product_attribute_id.id)])
                        if not attribute_value_id:
                            attribute_value_id = self.env["product.attribute.value"].create(
                                {"attribute_id": product_attribute_id.id,
                                 "name": value})
                            eg_attribute_value_id = self.env["eg.attribute.value"].create(
                                {"odoo_attribute_value_id": attribute_value_id.id,
                                 "inst_attribute_id": eg_product_attribute_id.id,
                                 "instance_id": instance_id.id,
                                 "odoo_attribute_id": product_attribute_id.id,
                                 })
                        else:
                            eg_attribute_value_id = self.env["eg.attribute.value"].create(
                                {"odoo_attribute_value_id": attribute_value_id.id,
                                 "inst_attribute_id": eg_product_attribute_id.id,
                                 "instance_id": instance_id.id,
                                 "odoo_attribute_id": product_attribute_id.id,
                                 })
                    else:
                        attribute_value_id = eg_attribute_value_id.odoo_attribute_value_id

                    value_list.append(attribute_value_id.id)
                    eg_value_list.append(eg_attribute_value_id.id)
                attribute_line_list.append((0, 0, {"attribute_id": product_attribute_id.id,
                                                   "value_ids": [(6, 0, value_list)]}))
                eg_attribute_line_list.append((0, 0, {"eg_product_attribute_id": eg_product_attribute_id.id,
                                                      "eg_value_ids": [(6, 0, eg_value_list)]}))

        return [attribute_line_list, eg_attribute_line_list]

    def export_product_mapping(self, response=None, eg_product_tmpl_id=None, instance_id=None):
        if response and eg_product_tmpl_id:
            product = response
            eg_product_tmpl_id.write({"inst_product_tmpl_id": str(product.get('id')),
                                      "update_required": False})
            attribute_list = []
            for option in product.get("options"):
                attribute_list.append(option.get("name"))
            for product_variant in product.get("variants"):
                value_list = []
                for option in ["option1", "option2", "option3"]:
                    if product_variant.get(option):
                        value_list.append(product_variant.get(option))
                eg_value_ids = self.env["eg.attribute.value"].search(
                    [("name", "in", value_list), ("instance_id", "=", instance_id.id),
                     ("inst_attribute_id.name", "=", attribute_list)])
                for eg_product_id in eg_product_tmpl_id.eg_product_ids:
                    if eg_product_id.eg_value_ids == eg_value_ids:
                        eg_product_id.write({"inst_product_id": str(product_variant.get("id")),
                                             "update_required": False,
                                             "inst_inventory_item_id": str(
                                                 product_variant.get("inventory_item_id"))})
                        break
        return True

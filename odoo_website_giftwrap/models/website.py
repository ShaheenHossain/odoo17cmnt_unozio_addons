# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import UserError
from odoo import models, fields, api
from odoo import http, SUPERUSER_ID, tools, _
from odoo.http import request
from stdnum.exceptions import ValidationError


class GiftWrapConfiguration(models.Model):
	_name = 'giftwrap.configuration'
	_rec_name = 'product_id'
	_description = 'giftwrap'
				
	product_id  = fields.Many2one('product.product','Product', domain = [('type', '=', 'service')])
	price  =  fields.Float('Price')
	journal_id = fields.Many2one(
		string="Payment Journal", comodel_name='account.journal',
		compute='_compute_journal_id', inverse='_inverse_journal_id',
		help="The journal in which the successful transactions are posted",
		domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]")

	@api.onchange('product_id')
	def _onchange_giftwrap(self):
		if self.product_id:
			self.update({
				'price': self.product_id.list_price,
			})

class websiteInherit(models.Model):
	_inherit = 'website'

	def get_website_giftwrap(self):  
		giftwrap_ids=self.env['giftwrap.configuration'].sudo().search([])
		return giftwrap_ids  

	def get_gift_product(self):
		giftwrap = self.env['giftwrap.configuration'].sudo().browse(self.id,product)
		return giftwrap  

class SaleInherit(models.Model):
	_inherit = 'sale.order'

	# @api.multi
	def _cart_updatenn(self, product_id=None, line_id=None, add_qty=0, set_qty=0, no_variant_attributes_price_extra=None,
					   order=None, product_custom_attribute_values=None, kw=None, _logger=None, **kwargs):
		""" Add or set product quantity, add_qty can be negative """
		self.ensure_one()
		product_context = dict(self.env.context)
		product_context.setdefault('lang', self.sudo().partner_id.lang)
		SaleOrderLineSudo = self.env['sale.order.line'].sudo().with_context(product_context)

		try:
			if add_qty:
				add_qty = float(add_qty)
		except ValueError:
			add_qty = 1
		try:
			if set_qty:
				set_qty = float(set_qty)
		except ValueError:
			set_qty = 0
		quantity = 0
		order_line = False
		if self.state != 'draft':
			request.session['sale_order_id'] = None
			raise UserError(_('It is forbidden to modify a sales order which is not in draft status.'))
		if line_id is not False:
			order_line = self._cart_find_product_line(product_id, line_id, **kwargs)[:1]

		# Create line if no line with product_id can be located
		if not order_line:
			# change lang to get correct name of attributes/values
			product = self.env['product.product'].with_context(product_context).browse(int(product_id))

			if not product:
				raise UserError(_("The given product does not exist therefore it cannot be added to cart."))

			no_variant_attribute_values = kwargs.get('no_variant_attribute_values') or []
			received_no_variant_values = product.env['product.template.attribute.value'].browse([int(ptav['value']) for ptav in no_variant_attribute_values])
			received_combination = product.product_template_attribute_value_ids | received_no_variant_values
			product_template = product.product_tmpl_id

			# handle all cases where incorrect or incomplete data are received
			combination = product_template._get_closest_possible_combination(received_combination)

			# get or create (if dynamic) the correct variant
			product = product_template._create_product_variant(combination)

			if not product:
				raise UserError(_("The given combination does not exist therefore it cannot be added to cart."))

			product_id = product.id

			values = order._cart_update(
				product_id=product_id,
				line_id=line_id,
				add_qty=add_qty,
				set_qty=set_qty,
				product_custom_attribute_values=product_custom_attribute_values,
				no_variant_attribute_values=no_variant_attribute_values,
				**kw
			)

			# add no_variant attributes that were not received
			for ptav in combination.filtered(lambda ptav: ptav.attribute_id.create_variant == 'no_variant' and ptav not in received_no_variant_values):
				no_variant_attribute_values.append({
					'value': ptav.id,
					'attribute_name': ptav.attribute_id.name,
					'attribute_value_name': ptav.name,
				})

			# save no_variant attributes values
			if no_variant_attribute_values:
				values['product_no_variant_attribute_value_ids'] = [
					(6, 0, [int(attribute['value']) for attribute in no_variant_attribute_values])
				]

			# add is_custom attribute values that were not received
			custom_values = kwargs.get('product_custom_attribute_values') or []
			received_custom_values = product.env['product.attribute.value'].browse([int(ptav['attribute_value_id']) for ptav in custom_values])

			for ptav in combination.filtered(lambda ptav: ptav.is_custom and ptav.product_attribute_value_id not in received_custom_values):
				custom_values.append({
					'attribute_value_id': ptav.product_attribute_value_id.id,
					'attribute_value_name': ptav.name,
					'custom_value': '',
				})

			# save is_custom attributes values
			if custom_values:
				values['product_custom_attribute_value_ids'] = [(0, 0, {
					'attribute_value_id': custom_value['attribute_value_id'],
					'custom_value': custom_value['custom_value']
				}) for custom_value in custom_values]

			# create the line
			order_line = SaleOrderLineSudo.create(values)
			# Generate the description with everything. This is done after
			# creating because the following related fields have to be set:
			# - product_no_variant_attribute_value_ids
			# - product_custom_attribute_value_ids
			order_line.name = order_line.get_sale_order_line_multiline_description_sale(product)

			try:
				order_line._compute_tax_id()
			except ValidationError as e:
				# The validation may occur in backend (eg: taxcloud) but should fail silently in frontend
				_logger.debug("ValidationError occurs during tax compute. %s" % (e))
			if add_qty:
				add_qty -= 1

		# compute new quantity
		if set_qty:
			quantity = set_qty
		elif add_qty is not None:
			quantity = order_line.product_uom_qty + (add_qty or 0)

		# Remove zero of negative lines
		if quantity <= 0:
			order_line.unlink()
		else:
			# update line
			no_variant_attributes_price_extra = [ptav.price_extra for ptav in order_line.product_no_variant_attribute_value_ids]
			if no_variant_attributes_price_extra.count(self) > 0:
				values = self.with_context(no_variant_attributes_price_extra=no_variant_attributes_price_extra)._website_product_id_change(self.id, product_id, qty=quantity)
				if self.pricelist_id.discount_policy == 'with_discount' and not self.env.context.get('fixed_price'):
					order = self.sudo().browse(self.id)
					product_context.update({
						'partner': order.partner_id,
						'quantity': quantity,
						'date': order.date_order,
						'pricelist': order.pricelist_id.id,
					})
					product = self.env['product.product'].with_context(product_context).browse(product_id)
					gift = self.env['giftwrap.configuration'].sudo().search([('product_id','=',product_id)])
					if gift:
						values['price_unit'] = gift.price
					else:
						values['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
						order_line._get_display_price(product),
						order_line.product_id.taxes_id,
						order_line.tax_id,
						self.company_id
					)

				order_line.write(values)
			else:
				print("There is no data")
		# link a product to the sales order
		if kwargs.get('linked_line_id'):
			linked_line = SaleOrderLineSudo.browse(kwargs['linked_line_id'])
			order_line.write({
				'linked_line_id': linked_line.id,
				'name': order_line.name + "\n" + _("Option for:") + ' ' + linked_line.product_id.display_name,
			})
			linked_line.write({"name": linked_line.name + "\n" + _("Option:") + ' ' + order_line.product_id.display_name})

		option_lines = self.order_line.filtered(lambda l: l.linked_line_id.id == order_line.id)
		for option_line_id in option_lines:
			self._cart_update(option_line_id.product_id.id, option_line_id.id, add_qty, set_qty, **kwargs)

		return {'line_id': order_line.id, 'quantity': quantity, 'option_ids': list(set(option_lines.ids))}                  
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    

# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from osv import osv, fields
import time
from datetime import datetime, date
from osv.orm import browse_record, browse_null
from osv.orm import except_orm
from tools.translate import _
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import decimal_precision as dp
import netsvc
import openerp
from pytz import timezone


class tms_agreement_line(osv.Model):
	_name = 'tms.agreement.line'
	_description = 'Agreement Line'


	def _amount_line(self, cr, uid, ids, field_name, args, context=None):
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		res = {}
		if context is None:
			context = {}
		for line in self.browse(cr, uid, ids, context=context):
			price = line.price_unit - line.price_unit *  (line.discount or 0.0) / 100.0
			taxes = tax_obj.compute_all(cr, uid, line.product_id.taxes_id, price, line.product_uom_qty, line.agreement_id.partner_invoice_id.id, line.product_id, line.agreement_id.partner_id)
			cur = line.agreement_id.currency_id

			amount_with_taxes = cur_obj.round(cr, uid, cur, taxes['total_included'])
			amount_tax = cur_obj.round(cr, uid, cur, taxes['total_included']) - cur_obj.round(cr, uid, cur, taxes['total'])
			
			price_subtotal = line.price_unit * line.product_uom_qty
			price_discount = price_subtotal * (line.discount or 0.0) / 100.0
			res[line.id] =  {   'price_total'   : amount_with_taxes,
								'price_amount': price_subtotal,
								'price_discount': price_discount,
								'price_subtotal': (price_subtotal - price_discount),
								'tax_amount'    : amount_tax,
								}
		return res



	_columns = {
		'agreement_id': openerp.osv.fields.many2one('tms.agreement', 'Agreement', required=False, ondelete='cascade', select=True, readonly=True),
		'line_type': openerp.osv.fields.selection([('product', 'Product'),('note', 'Note'),], 'Line Type', require=True),

		'name': openerp.osv.fields.char('Description', size=256, required=True),
		'sequence': openerp.osv.fields.integer('Sequence', help="Gives the sequence order when displaying a list of sales order lines."),
		'product_id': openerp.osv.fields.many2one('product.product', 'Product', 
							domain=[('sale_ok', '=', True),
									('tms_category', '=','freight'), 
									('tms_category', '=','move'), 
									('tms_category', '=','insurance'), 
									('tms_category', '=','highway_tolls'), 
									('tms_category', '=','other'),
									], change_default=True),
		'price_unit': openerp.osv.fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Sale Price')),
		'price_subtotal': openerp.osv.fields.function(_amount_line, method=True, string='Subtotal', type='float', digits_compute= dp.get_precision('Sale Price'),  store=True, multi='price_subtotal'),
		'price_amount': openerp.osv.fields.function(_amount_line, method=True, string='Price Amount', type='float', digits_compute= dp.get_precision('Sale Price'),  store=True, multi='price_subtotal'),
		'price_discount': openerp.osv.fields.function(_amount_line, method=True, string='Discount', type='float', digits_compute= dp.get_precision('Sale Price'),  store=True, multi='price_subtotal'),
		'price_total'   : openerp.osv.fields.function(_amount_line, method=True, string='Total Amount', type='float', digits_compute= dp.get_precision('Sale Price'),  store=True, multi='price_subtotal'),
		'tax_amount'   : openerp.osv.fields.function(_amount_line, method=True, string='Tax Amount', type='float', digits_compute= dp.get_precision('Sale Price'),  store=True, multi='price_subtotal'),
		'tax_id': openerp.osv.fields.many2many('account.tax', 'agreement_tax', 'agreement_line_id', 'tax_id', 'Taxes'),
		'product_uom_qty': openerp.osv.fields.float('Quantity (UoM)', digits=(16, 2)),
		'product_uom': openerp.osv.fields.many2one('product.uom', 'Unit of Measure '),
		'discount': openerp.osv.fields.float('Discount (%)', digits=(16, 2), help="Please use 99.99 format..."),
		'notes': openerp.osv.fields.text('Notes'),
		'agreement_partner_id': openerp.osv.fields.related('agreement_id', 'partner_id', type='many2one', relation='res.partner', store=True, string='Customer'),
		'salesman_id':openerp.osv.fields.related('agreement_id', 'user_id', type='many2one', relation='res.users', store=True, string='Salesman'),
		'company_id': openerp.osv.fields.related('agreement_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
		'control': openerp.osv.fields.boolean('Control'),
	}
	_order = 'sequence, id desc'

	_defaults = {
		'line_type': 'product',
		'discount': 0.0,
		'product_uom_qty': 1,
		'sequence': 10,
		'price_unit': 0.0,
	}


	def on_change_product_id(self, cr, uid, ids, product_id):
		res = {}
		if not product_id:
			return {}
		prod_obj = self.pool.get('product.product')
		for product in prod_obj.browse(cr, uid, [product_id], context=None):
			
			for x in product.taxes_id:
				print x.id
			res = {'value': {'product_uom' : product.uom_id.id,
							 'name': product.name,
							 'tax_id': [(6, 0, [x.id for x in product.taxes_id])],
							}
				}
		return res

	def on_change_amount(self, cr, uid, ids, product_uom_qty, price_unit, discount, product_id):
		res = {'value': {
					'price_amount': 0.0, 
					'price_subtotal': 0.0, 
					'price_discount': 0.0, 
					'price_total': 0.0,
					'tax_amount': 0.0, 
						}
				}
		if not (product_uom_qty and price_unit and product_id ):
			return res
		tax_factor = 0.00
		prod_obj = self.pool.get('product.product')
		for line in prod_obj.browse(cr, uid, [product_id], context=None)[0].taxes_id:
			tax_factor = (tax_factor + line.amount) if line.amount <> 0.0 else tax_factor
		price_amount = price_unit * product_uom_qty
		price_discount = (price_unit * product_uom_qty) * (discount/100.0)
		res = {'value': {
					'price_amount': price_amount, 
					'price_discount': price_discount, 
					'price_subtotal': (price_amount - price_discount), 
					'tax_amount': (price_amount - price_discount) * tax_factor, 
					'price_total': (price_amount - price_discount) * (1.0 + tax_factor),
						}
				}
		return res

tms_agreement_line()
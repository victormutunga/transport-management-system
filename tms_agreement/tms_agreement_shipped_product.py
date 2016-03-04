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


class tms_agreement_shipped_product(osv.Model):
	_name = 'tms.agreement.shipped_product'
	_description = 'Agreement Shipped Product'


	_columns = {
		'agreement_id': openerp.osv.fields.many2one('tms.agreement', 'Agreement', required=False, ondelete='cascade', select=True, readonly=True),
		'name': openerp.osv.fields.char('Description', size=256, required=True, select=True),
		'product_id': openerp.osv.fields.many2one('product.product', 'Product', 
							domain=[
									('tms_category', '=','transportable'), 
									('tms_category', '=','move'), 
									('tms_category', '=','insurance'), 
									('tms_category', '=','highway_tolls'), 
									('tms_category', '=','other'),
									], change_default=True, required=True),
		'product_uom': openerp.osv.fields.many2one('product.uom', 'Unit of Measure ', required=True),
		'product_uom_qty': openerp.osv.fields.float('Quantity (UoM)', digits=(16, 2), required=True),
		'notes': openerp.osv.fields.text('Notes'),
		'agreement_partner_id': openerp.osv.fields.related('agreement_id', 'partner_id', type='many2one', relation='res.partner', store=True, string='Customer'),
		'salesman_id':openerp.osv.fields.related('agreement_id', 'user_id', type='many2one', relation='res.users', store=True, string='Salesman'),
		'shop_id': openerp.osv.fields.related('agreement_id', 'shop_id', type='many2one', relation='sale.shop', string='Shop', store=True, readonly=True),
		'company_id': openerp.osv.fields.related('agreement_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
		'sequence': openerp.osv.fields.integer('Sequence', help="Gives the sequence order when displaying a list of sales order lines."),
	}
	_order = 'sequence, id desc'
	_defaults = {
		'product_uom_qty': 1,
		'sequence': 10,
	}

	def on_change_product_id(self, cr, uid, ids, product_id):
		res = {}
		if not product_id:
			return {}
		prod_obj = self.pool.get('product.product')
		for product in prod_obj.browse(cr, uid, [product_id], context=None):            
			res = {'value': {'product_uom' : product.uom_id.id,
							 'name': product.name}
				}
		return res



tms_agreement_shipped_product()
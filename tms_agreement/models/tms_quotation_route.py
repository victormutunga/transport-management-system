# -*- encoding: utf-8 -*-
##############################################################################
#	
#	OpenERP, Open Source Management Solution
#	Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.	 
#
##############################################################################

from osv import osv, fields
import time
import dateutil
import dateutil.parser
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, time, timedelta
from tools.translate import _
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import decimal_precision as dp
import netsvc
import openerp
import calendar
from pytz import timezone


class tms_quotation_route(osv.Model):
	_name = 'tms.quotation.route'
	_description = 'Quotations Routes for TMS QUOTATION'

	def _get_total(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		total = 0.0
		for factor in self.browse(cr, uid, ids, context=context):
			if factor.factor_type != 'special':
				res[factor.id] = factor.factor * factor.variable_amount + (factor.fixed_amount if factor.mixed else 0.0)
			else: 
				res[factor.id] = 0.0 # Pendiente generar cálculo especial
		return res

	_columns = {
		'name': fields.char('Description of the Route', size=128, required=False),
		'quotation_id': fields.many2one('tms.quotation', 'Quotation ID', ondelete='cascade'),			  
		'route_id': fields.many2one('tms.route', 'Route', required=True),
		'kms': fields.float('Kms', digits=(4,2), required=True),
		'product_id': fields.many2one('product.product', 'Product', domain=['|','|','|','|',
									('tms_category', '=','transportable'), 
									('tms_category', '=','move'), 
									('tms_category', '=','insurance'), 
									('tms_category', '=','highway_tolls'), 
									('tms_category', '=','other'),
									], change_default=True),
		'product_weight': fields.float('Weight', digits=(16, 2)),
		'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True),
		'rate': fields.float('Rate', digits=(16, 2)),
		'insurance': fields.float('Insurance', digits=(16, 2), required=True),
		'income': fields.float('Income', digits=(16, 2), required=True),
		'uncharged': fields.boolean('Uncharged'),
		'mark': fields.boolean('Mark'),
		'notes': fields.text('Notes'),

		########### --- CAMPOS NECESARIOS PARA EL FACTOR --- #############
		# 'category'	  : fields.selection([

		# 								('driver', 'Driver'),
		# 								('customer', 'Customer'),
		# 								('supplier', 'Supplier'),
		# 								], 'Type', required=True),
		'factor_type'   : fields.selection([
										('default','Default'),
										('distance', 'Distance Route (Km/Mi)'),
										('weight', 'Weight'),
										('travel', 'Travel'),
										('qty', 'Quantity'),
										], 'Factor Type', required=False, help="""
For next options you have to type Ranges or Fixed Amount
 - Distance Route (Km/mi)
 - Weight
 - Quantity
 - Volume
For next option you only have to type Fixed Amount:
 - Travel
For next option you only have to type Factor like 10.5 for 10.50%:

						"""),
		
		'framework'	 : fields.selection([
								('Any', 'Any'),
								('Unit', 'Unit'),
								('Single', 'Single'),
								('Double', 'Double'),
								], 'Framework', required=True),
		# 'factor'		: fields.float('Factor',		digits=(16, 4)),
		#### EL FACTOR ES EL RATE ####
		'fixed_amount'  : fields.float('Fixed Amount', digits=(16, 4)),
		'mixed'		 : fields.boolean('Mixed'),
		'total_amount'  : fields.function(_get_total, method=True, digits_compute=dp.get_precision('Sale Price'), string='Total', type='float', store=True),
		'variable_amount' : fields.float('Variable',  digits=(16, 4)),
		'sequence'	  : fields.integer('Sequence', help="Gives the sequence calculation for these factors."),											
	}

	_defaults = {
		'mixed'			 : False,
		'sequence'	 	 : 10,
		'framework'		 : 'Any',
		'factor_type'    : 'default',
		
	}

	def calculate(self, cr, uid, ids, factor_type, total_kms, total_weight, factor, mixed, fixed_amount, context=None):
		result = 0.0
		x = 0.0
		if factor_type == 'distance': 
			print "Tipo Distancia"

			x = (float(total_kms))

		elif factor_type == 'weight':
			print "####### TIPO PESO"

			x = float(total_weight)

		elif factor_type == 'qty':
			print "####### TIPO CANTIDAD"
			x = float(total_weight)

		elif factor_type == 'travel':
			print "####### TIPO VIAJE"
			x = 0.0
		
		result += ((fixed_amount if (mixed or factor_type=='travel') else 0.0)+ (factor * x ))
		print "fixed_amount : ", fixed_amount
		print "mixed : ", mixed
		print "factor_type : ", factor_type
		print "factor : ", factor
		print "x : ", x
		print "################################################# RESULTADO =================", result
		print "################################################# RESULTADO =================", result
		return result
		

	def onchange_route(self, cr, uid, ids, route_id, context=None):
		if not route_id:
			return {'value': {} }
		route_obj = self.pool.get('tms.route')
		kms = 0.0
		for r in route_obj.browse(cr, uid, [route_id]):
			kms = r.distance
		val = {
			'kms': kms,
		}
		return {'value': val}

	def onchange_quotation(self, cr, uid, ids, factor_type, kms, product_weight, rate, insurance, mixed, fixed_amount, context=None):
		print "##################################### KMS", kms
		print "##################################### PRODUCT WEIGHT", product_weight
		print "##################################### RATE", rate
		print "##################################### INSURANCE", insurance
		print "##################################### FACTOR TYPE", factor_type
		print "##################################### MIXED", mixed
		print "##################################### FIXED AMOUNT", fixed_amount
		total = 0.0
		if factor_type == 'default':
			total = (product_weight * rate)+insurance
		if not factor_type:
			total = 0.0 + insurance
		else:
			calculate = self.calculate(cr, uid, ids, factor_type, kms, product_weight, rate, mixed, fixed_amount)
			print "############################################################ CALCULATE", calculate
			print "############################################################ CALCULATE", calculate
			print "############################################################ CALCULATE", calculate
			total = calculate + insurance
		print "################################################################ AL FINAL EL TOTAL ES", total
		val = {
			'income': total,
		}
		return {'value': val}

	def onchange_unchanged(self, cr, uid, ids, uncharged, context=None):
		if uncharged == True:
			val = {
				"product_id": False,
				"product_weight" : 0.0,
				"product_uom": 0.0,
				"rate" : 0.0,
				"factor_type": False,
				"mixed": False,
				"fixed_amount": 0.0,
				#"income": 0.0
			}
		return {'value': val}

	_order = "name"

	def onchange_product_id(self, cr, uid, ids, product_id, context=None):
		product_obj = self.pool.get('product.product')
		if product_id:
			for product in product_obj.browse(cr, uid, [product_id], context=context):

				val = {
						'product_uom': product.uom_id.id,
					}
		else:
			val = {}
		return {'value':val}

tms_quotation_route()
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
# Extra data fields for Waybills & Agreement
# Factors

class factor_quotation(osv.osv):
	_name = "factor.quotation"
	_description = "Factors to calculate Payment Client charge"

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
		'name'		  : fields.char('Name', size=64, required=True),
		'category'	  : fields.selection([
										('driver', 'Driver'),
										('customer', 'Customer'),
										('supplier', 'Supplier'),
										], 'Type', required=True),

		'factor_type'   : fields.selection([
										('distance', 'Distance Route (Km/Mi)'),
										('distance_real', 'Distance Real (Km/Mi)'),
										('weight', 'Weight'),
										('travel', 'Travel'),
										('qty', 'Quantity'),
										('volume', 'Volume'),
										('percent', 'Income Percent'),
										('special', 'Special'),
										], 'Factor Type', required=True, help="""
For next options you have to type Ranges or Fixed Amount
 - Distance Route (Km/mi)
 - Distance Real (Km/Mi)
 - Weight
 - Quantity
 - Volume
For next option you only have to type Fixed Amount:
 - Travel
For next option you only have to type Factor like 10.5 for 10.50%:
 - Income Percent
For next option you only have to type Special Python Code:
 - Special
						"""),
		
		'framework'	 : fields.selection([
								('Any', 'Any'),
								('Unit', 'Unit'),
								('Single', 'Single'),
								('Double', 'Double'),
								], 'Framework', required=True),

		'range_start'   : fields.float('Range Start',   digits=(16, 4)),
		'range_end'	 : fields.float('Range End',	 digits=(16, 4)),
		'factor'		: fields.float('Factor',		digits=(16, 4)),
		'fixed_amount'  : fields.float('Fixed Amount', digits=(16, 4)),
		'mixed'		 : fields.boolean('Mixed'),
		'factor_special_id': fields.many2one('tms.factor.special', 'Special'),

        'expense_id'    : fields.many2one('tms.expense', 'Expense', required=False, ondelete='cascade'), #, select=True, readonly=True),
        'route_id'      : fields.many2one('tms.route',   'Route', required=False, ondelete='cascade'), #, select=True, readonly=True),
        'travel_id'     : fields.many2one('tms.travel', 'Travel', required=False, ondelete='cascade'), #, select=True, readonly=True),

		'variable_amount' : fields.float('Variable',  digits=(16, 4)),
		'total_amount'  : fields.function(_get_total, method=True, digits_compute=dp.get_precision('Sale Price'), string='Total', type='float',
											store=True),
		'sequence'	  : fields.integer('Sequence', help="Gives the sequence calculation for these factors."),
		'notes'		 : fields.text('Notes'),
		'control'	   : fields.boolean('Control'),
        'driver_helper' : fields.boolean('For Driver Helper'),
		'quotation_id': fields.many2one('tms.quotation', 'Quotation ID'),
		'agreement_id': fields.many2one('tms.agreement', 'Agreement ID'),
	}

	_defaults = {
		'mixed'			 : False,
		'sequence'		  : 10,
		'variable_amount'   : 0.0,
		'framework'		 : 'Any',
		'category'		  : 'customer',
	}

	_order = "sequence"

	def on_change_factor_type(self, cr, uid, ids, factor_type):
		if not factor_type:
			return {'value': {'name': False}}
		values = {
					'distance'  : _('Distance Route (Km/Mi)'),
					'distance_real'  : _('Distance Real (Km/Mi)'),
					'weight'	: _('Weight'),
					'travel'	: _('Travel'),
					'qty'	   : _('Quantity'),
					'volume'	: _('Volume'),
					'percent'   : _('Income Percent'),
					'special'   : _('Special'),
			}
		return {'value': {'name': values[factor_type]}}

	def calculate(self, cr, uid, record_type, record_ids, context=None):
		result = 0.0
		if record_type == 'agreement':
			#print "==================================="
			#print "Calculando"
			agreement_obj = self.pool.get('tms.agreement')
			for agreement in agreement_obj.browse(cr, uid, record_ids, context=context):  # No soporta segundo operador
				print "Recorriendo Agreements"
				for factor in (agreement.agreement_customer_factor if calc_type=='client' else agreement.agreement_driver_factor if calc_type=='driver' else agreement.agreement_supplier_factor):
					print "Recorriendo factors"
					print "Tipo de factor: ", factor.factor_type
					if factor.factor_type in ('distance', 'distance_real'): 
						print "Tipo Distancia"
						if not agreement.route_id:
							raise osv.except_osv(
								_('Could calculate Amount for Agreement !'),
								_('Agreement %s is not assigned to Route') % (agreement.name))
						print agreement.route_id.distance
						x = (float(agreement.route_id.distance) if factor.factor_type=='distance' else 0.0)

					elif factor.factor_type == 'weight':
						product_weight = 0.0
						for weight in agreement.agreement_shipped_product:
							product_weight += weight.product_uom_qty
						print "agreement.product_weight", product_weight
						if product_weight <= 0.0:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with UoM Category = Weight or Product Qty = 0.0' % agreement.name))

						x = float(product_weight)

					elif factor.factor_type == 'qty':
						product_weight = 0.0
						for weight in agreement.agreement_shipped_product:
							product_weight += weight.product_uom_qty
						print "agreement.product_weight", product_weight
						if product_weight <=0.0 :
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with Quantity > 0.0') % (agreement.name))

						x = float(product_weight)

					elif factor.factor_type == 'volume':
						product_weight = 0.0
						for weight in agreement.agreement_shipped_product:
							product_weight += weight.product_uom_qty
						print "agreement.product_weight", product_weight
						if product_weight <=0.0 :
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with UoM Category = Volume or Product Qty = 0.0') % (agreement.name))

						x = float(product_weight)

					elif factor.factor_type == 'percent':
						x = float(agreement.amount_subtotal) / 100.0

					elif factor.factor_type == 'travel':
						x = 0.0

					elif factor.factor_type == 'special':
						exec factor.factor_special_id.python_code

					
					result += ((factor.fixed_amount if (factor.mixed or factor.factor_type=='travel') else 0.0)+ (factor.factor * x if factor.factor_type != 'special' else x)) if (((x >= factor.range_start and x <= factor.range_end) or (factor.range_start == factor.range_end == 0.0)) and factor.driver_helper==driver_helper) else 0.0
					#print "factor.fixed_amount : ", factor.fixed_amount
					#print "factor.mixed : ", factor.mixed
					#print "factor.factor_type : ", factor.factor_type
					#print "factor.factor : ", factor.factor
					#print "x : ", x
					print "################################################# RESULTADO =================", result
					print "################################################# RESULTADO =================", result
		return result
	
factor_quotation()

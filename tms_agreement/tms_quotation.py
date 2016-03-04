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


class tms_quotation(osv.Model):
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_name = 'tms.quotation'
	_rec_name = 'sequence'
	_description = 'Quotations for TMS'

	def copy(self, cr, uid, id, default=None, context=None):
		if not default:
			default = {}
		default.update({
			'sequence': self.pool.get('ir.sequence').get(cr, uid, 'tms.quotation'),
		})
		return super(tms_quotation, self).copy(cr, uid, id, default, context=context)


	def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
		cur_obj = self.pool.get('res.currency')
		res = {}
		for quotation in self.browse(cr, uid, ids, context=context):
			res[quotation.id] = {
				'operating_amount_all': 0.0,
				'administrative_amount_all': 0.0,

			}
			operating_amount_all = 0.0
			administrative_amount_all = 0.0

			for operating in quotation.operating_cost_ids:
				operating_amount_all += operating.travel_days

			for administrative in quotation.administrative_expenses_ids:
				administrative_amount_all += administrative.travel_days
			res[quotation.id]['operating_amount_all'] = operating_amount_all
			res[quotation.id]['administrative_amount_all'] = administrative_amount_all

		return res
	_columns = {
		'name': fields.char('Description of the Route', size=128, required=True),
		'partner_id': fields.many2one('res.partner', 'Customer', required=True, readonly=False),
		'agreement_id': fields.many2one('tms.agreement', 'Agreement', readonly=True, help="Representa el Acuerdo que se genero a partir de esta Cotizacion"),
		'type_armed': fields.selection([('tractor','Drive Unit'), ('one_trailer','Single Trailer'), ('two_trailer','Double Trailer')], 'Type of Armed', required=True),
		'days': fields.integer('Travel Days', required=True),
		'month_travel': fields.float('Month Travels', digits=(4,2), required=True), # Este campo se debe calcular por onchange o por funcion al guardar
		'total_kms': fields.float('Total Kms', digits=(4,2), readonly=True), # Este campo se debe calcular por onchange o por funcion al guardar
		'total_tons': fields.float('Total Tonnes', digits=(4,2), readonly=True), # Este campo se debe calcular por onchange o por funcion al guardar
		'total_security': fields.float('Total Insurance', digits=(4,2), readonly=True), # Este campo se debe calcular por onchange o por funcion al guardar
		'total_ingr': fields.float('Total Income', digits=(4,2), readonly=True), # Este campo se debe calcular por onchange o por funcion al guardar
		'unit_ids': fields.many2one('tms.unit.category', 'Unit Category',required=False),

		############ ---  ROUTES FOR QUOTATION --- ############
		'route_ids': fields.one2many('tms.quotation.route','quotation_id'),
		'sequence': fields.char('Sequence', size=64),

		############ --- PARAMETERS ---######################
		'parameter_id': fields.many2one('tms.quotation.config', 'Parameters', required=True),

		########### ---- COSTOS FIJOS OPERATIVOS ---- #########
		'operating_cost_ids': fields.one2many('tms.operating.cost', 'quotation_id' ,'Fixed Operating Costs'),
		'load_operating_cost': fields.boolean('Cargar Costos Operativos Automaticamente'),
		'amount_acumulated_fixed': fields.float('Amount Acumulated Fixed', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_monthly_fixed': fields.float('Amount Acumulated Monthly', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_daily_fixed': fields.float('Amount Acumulated Daily', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_travel_days_fixed': fields.float('Amount Acumulated Travel Days', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_percentage_fixed': fields.float('Amount Acumulated Percentage', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena

		######### ---- SUMATORIA DE LOS GASTOS FIJOS Y ADMINISTRATIVOS ---- #######
		'operating_amount_all': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'),string='Operating Amount', multi='sums', store=True),
		'administrative_amount_all': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'),string='Administratives Exenses Amount', multi='sums', store=True),

		########### ---- COSTOS VARIABLES OPERATIVOS ---- #########
		'diesel_cost': fields.float('Cost of Diesel', digits=(9,2), required=True),
		'diesel_mtto_monthly': fields.char('Daily Average', size=0, readonly=False),
		'diesel_mtto_travel_days': fields.char('Travel Days', size=0, readonly=False),
		'diesel_mtto_percent': fields.char('%', digits=(9,2), size=0, readonly=False),

		'factor_mtto': fields.float('Maintenance Factor', digits=(9,2), required=True),
		'factor_mtto_monthly': fields.float('Daily Average', digits=(9,2), required=False, help="Maintenance Factor Daily Average"),
		'factor_mtto_travel_days': fields.float('Travel Days', digits=(9,2), required=False, help="Maintenance Factor Travel Days"),
		'factor_mtto_percent': fields.float('%', digits=(9,2), required=False, help="Maintenance Factor %"),

		'factor_tires': fields.float('Tires Factor', digits=(9,2), required=True),
		'factor_tires_monthly': fields.float('Daily Average', digits=(9,2), required=False, help="Tires Factor Daily Average"),
		'factor_tires_travel_days': fields.float('Travel Days', digits=(9,2), required=False, help="TiresFactor Travel Days"),
		'factor_tires_percent': fields.float('%', digits=(9,2), required=False, help="Tires Factor %"),

		'performance_loaded': fields.float('Performance Loaded', digits=(9,2), required=True),
		'uncharged_performance': fields.float('Uncharged Performance', digits=(9,2), required=True),

		'liters_diesel': fields.float('Liters of Diesel', digits=(9,2), required=True),

		'money_diesel': fields.char('$ Diesel', size=0, readonly=True),
		'amount_total_diesel': fields.float('$ Diesel', digits=(9,2), required=False),
		'diesel_monthly': fields.float('Daily Average', digits=(9,2), required=False),
		'diesel_travel_days': fields.float('Travel Days', digits=(9,2), required=False),
		'diesel_percent': fields.float('Percentage', digits=(9,2), required=False),

		'total_highway_toll': fields.float('Highway Tolls', digits=(9,2), required=True), #### Se calculara en base a las casetas que se tengan definidas en cada ruta
		'toll_monthly': fields.float('Daily Average', digits=(9,2), required=False),
		'toll_travel_days': fields.float('Travel Days', digits=(9,2), required=False),
		'toll_percent': fields.float('Percentage', digits=(9,2), required=False),

		'operator_salary': fields.float('Operator Salary', digits=(9,2), required=False), #### Se calculara en base al sueldo definido en cada ruta
		'salary_monthly': fields.float('Daily Average', digits=(9,2), required=False),
		'salary_travel_days': fields.float('Travel Days', digits=(9,2), required=False),
		'salary_percent': fields.float('Percentage', digits=(9,2), required=False),

		'move_amount': fields.float('Shunting', digits=(9,2), required=False), #### Se calculara en base al sueldo definido en cada ruta
		'move_monthly': fields.float('Daily Average', digits=(9,2), required=False),
		'move_travel_days': fields.float('Travel Days', digits=(9,2), required=False),
		'move_percent': fields.float('Percentage', digits=(9,2), required=False),

		'amount_daily_variable': fields.float('Total Daily', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_travel_days_variable': fields.float('Total Travel Days', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_percentage_variable': fields.float('Total %', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena

		######## ---- GASTOS ADMINISTRATIVOS ----- ################
		'administrative_expenses_ids': fields.one2many('tms.administrative.cost', 'quotation_id' ,'Administrative Expenses'),
		'load_administrative_expenses': fields.boolean('Cargar Gastos Administrativos'),
		'amount_acumulated_administrative': fields.float('Amount Acumulated Fixed', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_monthly_administrative': fields.float('Amount Acumulated Monthly', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_daily_administrative': fields.float('Amount Acumulated Daily', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_travel_days_administrative': fields.float('Amount Acumulated Travel Days', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_percentage_administrative': fields.float('Amount Acumulated Percentage', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena

		####### ---- SUMMARY ----- ########
		'summary_income_monthly': fields.float('Daily Average', digits=(9,2) ),
		'summary_income_travel_days': fields.float('Travel Days', digits=(9,2) ),
		'summary_income_percent': fields.float('Percentage', digits=(3,2) ),

		'summary_expenditures_monthly': fields.float('Daily Average', digits=(9,2) ),
		'summary_expenditures_travel_days': fields.float('Travel Days', digits=(9,2) ),
		'summary_expenditures_percent': fields.float('Percentage', digits=(3,2) ),

		'summary_utility_monthly': fields.float('Daily Average', digits=(9,2) ),
		'summary_utility_travel_days': fields.float('Travel Days', digits=(9,2) ),
		'summary_utility_percent': fields.float('Percentage', digits=(3,2) ),

		'summary_km_productive_monthly': fields.float('Daily Average', digits=(9,2) ),
		'summary_km_productive_travel_days': fields.float('Travel Days', digits=(9,2) ),
		'summary_km_productive_percent': fields.float('Percentage', digits=(3,2) ),

		'summary_mk_shot_monthly': fields.float('Daily Average', digits=(9,2) ),
		'summary_mk_shot_travel_days': fields.float('Travel Days', digits=(9,2) ),
		'summary_mk_shot_percent': fields.float('Percentage', digits=(3,2) ),

		'summary_cost_km_monthly': fields.float('Daily Average', digits=(9,2) ),
		'summary_cost_km_travel_days': fields.float('Travel Days', digits=(9,2) ),
		'summary_cost_km_percent': fields.float('Percentage', digits=(3,2) ),

		'summary_utility_km_monthly': fields.float('Daily Average', digits=(9,2) ),
		'summary_utility_km_travel_days': fields.float('Travel Days', digits=(9,2) ),
		'summary_utility_km_percent': fields.float('Percentage', digits=(3,2) ),

		'summary_margin_monthly': fields.float('Daily Average', digits=(9,2) ),
		'summary_margin_travel_days': fields.float('Travel Days', digits=(9,2) ),
		'summary_margin_percent': fields.float('Percentage', digits=(3,2) ),


		####### --- Notas ----- #############
		'notes': fields.text('Notes'),
		'state': fields.selection([('draft','Draft'), ('confirmed','Confirmed'), ('done','Done'), ('cancel','Cancelled')], 'Quotation State', readonly=True),

		###### ---- FACTORES ---- ######
		#'factor_ids': fields.one2many('factor.quotation', 'quotation_id', 'Factors Quote'),

		###### ---- DATOS PARA LA VISTA KANBAN ---- ########
		'image': fields.related('partner_id', 'image', type="binary", string="Logo", readonly=True),
		'image_medium': fields.related('partner_id', 'image_medium', type="binary", string="Logo"),
		'image_small': fields.related('partner_id', 'image_small', type="binary", string="Logo"),
		'currency_id': fields.many2one('res.currency','Currency',states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}, required=True),


	}


	def _get_parameter(self,cr,uid,context=None): # esta funcion en el wizard le va agregar por defecto la session en la que estamos
		parameter_obj = self.pool.get('tms.quotation.config')
		parameter_ids = parameter_obj.search(cr, uid, [('active','=',True)], limit=1)
		if not parameter_ids:
			raise osv.except_osv(
						_('Error !'),
						_('Configuration Error Found no Predefined Parameters !!!'))
		return parameter_ids[0]

	_defaults = {
	#'sequence': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'tms.quotation'),
	'type_armed': 'tractor',
	'parameter_id': _get_parameter,
	'days': 1,
	'state': 'draft',
	'load_operating_cost': True,
	'load_administrative_expenses': True,
	'currency_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.currency_id.id,

	}

	_order = "sequence desc"

	def create(self, cr, uid, vals, context=None):
		seq_number = self.pool.get('ir.sequence').get(cr, uid, 'tms.quotation'),
		vals['sequence'] = seq_number[0]
		return super(tms_quotation, self).create(cr, uid, vals, context=context)

	def action_calculate(self, cr, uid, ids, context=None):
		product_obj = self.pool.get('product.product')
		for rec in self.browse(cr, uid, ids, context=context):
			total_kms = 0.0
			total_income = 0.0
			total_insurance = 0.0
			total_tons = 0.0
			for routes in rec.route_ids:
				total_kms += routes.kms
				total_tons += routes.product_weight
				total_insurance += routes.insurance
				# if not rec.factor_ids:
				total_income += routes.income
				# else:
				# 	for factor in rec.factor_ids:
				# 		factor_obj = self.pool.get('factor.quotation')
				#		total_income = factor_obj.calculate(cr, uid, 'quotation', ids, context) 
			rec.write({ 'total_kms': total_kms, 'total_tons': total_tons, 'total_security': total_insurance,'total_ingr': total_income})

			# for factor in rec.factor_ids:
			# 	factor_obj = self.pool.get('factor.quotation')
			# 	total_income = factor_obj.calculate(cr, uid, 'quotation', ids, context) 

			total_acumulated_fixed = 0.0
			total_acumulated_monthly = 0.0
			total_acumulated_dailt = 0.0
			total_acumulated_days = 0.0
#			total_acumulated_percentage = 0.0
			for fixes in rec.operating_cost_ids:
				total_acumulated_fixed += fixes.acumulated_moth
				total_acumulated_monthly += fixes.average_moth
				total_acumulated_dailt += fixes.daily_average
				travel_days = fixes.daily_average * rec.days
				fixes.write({'travel_days':travel_days})
				total_acumulated_days += travel_days
#				total_acumulated_percentage += fixes.percent
			rec.write({ 'amount_acumulated_fixed': total_acumulated_fixed, 
						'amount_monthly_fixed': total_acumulated_monthly, 
						'amount_daily_fixed': total_acumulated_dailt, 
						'amount_travel_days_fixed': total_acumulated_days, 
						#'amount_percentage_fixed': total_acumulated_percentage
						})

			########### ---- COSTOS VARIABLES OPERATIVOS ---- #########
			#### OBTENIENDO LOS COSTOS VARIABLES
			factor_mtto_travel_days = rec.factor_mtto * total_kms
			factor_mtto_monthly = factor_mtto_travel_days / rec.days
			factor_tires_travel_days = rec.factor_tires * total_kms
			factor_tires_monthly = factor_tires_travel_days / rec.days
			performance_loaded = 0.0
			uncharged_performance = 0.0
			
			for performance in rec.route_ids:
				if performance.uncharged == True or performance.product_weight == 0.0:
					result_loader = performance.kms / rec.uncharged_performance
					performance_loaded += result_loader
				elif performance.uncharged == False or performance.product_weight > 0.0:
					result_uncharged = performance.kms / rec.performance_loaded
					performance_loaded += result_uncharged
			performance_total = performance_loaded + uncharged_performance

			diesel_travel_days = performance_total * rec.diesel_cost
			diesel_monthly = diesel_travel_days / rec.days
#			diesel_percent = (rec.total_ingr/performance_total) * 100

			rec.write({ 'factor_mtto_monthly': factor_mtto_monthly, 
						'factor_mtto_travel_days': factor_mtto_travel_days, 
						'factor_tires_travel_days': factor_tires_travel_days, 
						'factor_tires_monthly': factor_tires_monthly, 
						'liters_diesel': performance_total,
						'diesel_travel_days' : diesel_travel_days,
						'diesel_monthly': diesel_monthly,
#						'diesel_percent': 0.0,

						})

			####### ---- CALCULANDO LAS CASETAS ---- ###################

			total_highway_toll = 0.0

			for highway in rec.route_ids:
				amount_axis_credit = 0.0
				amount_axis = 0.0
				for toll in highway.route_id.tms_route_tollstation_ids:
					if toll.credit:
						for axis in toll.tms_route_tollstation_costperaxis_ids:
							if axis.unit_type_id.id == rec.unit_ids.id:
								amount_axis_credit += axis.cost_credit
					else:
						for axis in toll.tms_route_tollstation_costperaxis_ids:
							if axis.unit_type_id.id == rec.unit_ids.id:
								amount_axis_credit += axis.cost_cash

					amount_toll_station_route = amount_axis_credit + amount_axis
					total_highway_toll += amount_toll_station_route

			if rec.total_highway_toll <=0.0:
				total_highway_toll = total_highway_toll
			elif rec.total_highway_toll != total_highway_toll:
				total_highway_toll = rec.total_highway_toll

			toll_monthly = 0.0
#			toll_percent = 0.0
			if total_highway_toll > 0.0 :
				toll_monthly = total_highway_toll / rec.days

			rec.write({ 'total_highway_toll': total_highway_toll if total_highway_toll > 0.0 else 0.0,
						'toll_travel_days': total_highway_toll if total_highway_toll > 0.0 else 0.0,
						'toll_monthly': toll_monthly,
#						'toll_percent': toll_percent,
						})

			###### ---- CALCULANDO EL FACTOR OPERADOR --- #####
			operator_salary = 0.0

			for quotation in rec.route_ids:
				result = 0.0
				for factor in (quotation.route_id.expense_driver_factor):
					if factor.factor_type in ('distance', 'distance_real'):
						if not quotation.route_id.id:
							raise osv.except_osv(
								_('Could calculate Freight amount for quotation !'),
								_('quotation %s is not assigned to a Travel') % (quotation.name))
						x = (float(quotation.route_id.distance) if factor.factor_type=='distance' else float(quotation.route_id.distance_extraction))
						#x = (float(quotation.route_id.distance) if factor.factor_type=='distance' else float(quotation.route_id.distance_extraction)) if factor.framework == 'Any' else 0.0

					elif factor.factor_type == 'weight':
						if not quotation.product_weight:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('quotation %s has no Products with UoM Category = Weight or Product Qty = 0.0' % quotation.name))

						x = float(quotation.product_weight)

					elif factor.factor_type == 'qty':
						if not quotation.product_qty:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('quotation %s has no Products with Quantity > 0.0') % (quotation.name))

						x = float(quotation.product_qty)

					elif factor.factor_type == 'volume':
						if not quotation.product_volume:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('quotation %s has no Products with UoM Category = Volume or Product Qty = 0.0') % (quotation.name))

						x = float(quotation.product_volume)

					elif factor.factor_type == 'percent':
						x = float(quotation.amount_freight) / 100.0

					elif factor.factor_type == 'travel':
						x = 0.0

					elif factor.factor_type == 'special':
						exec factor.factor_special_id.python_code

					result += ((factor.fixed_amount if (factor.mixed or factor.factor_type=='travel') else 0.0) + (factor.factor * x if factor.factor_type != 'special' else x)) if ((x >= factor.range_start and x <= factor.range_end) or (factor.range_start == factor.range_end == 0.0)) else 0.0

					operator_salary += result

			if rec.operator_salary <= 0.0 :
				operator_salary = operator_salary
			elif rec.operator_salary != operator_salary:
				operator_salary = rec.operator_salary
			salary_monthly = 0.0
#			salary_percent = 0.0
			if operator_salary > 0.0:
				salary_monthly = operator_salary / rec.days

			rec.write({ 'operator_salary': operator_salary if operator_salary > 0.0 else 0.0,
						'salary_travel_days': operator_salary if operator_salary > 0.0 else 0.0,
						'salary_monthly': salary_monthly,
#						'salary_percent': salary_percent,
						})

			######## -----  MANIOBRAS ----- ########

			move_amount = rec.move_amount
			move_monthly = 0.0
#			move_percent = 0.0
			if move_amount > 0.0:
				move_monthly = move_amount / rec.days

			rec.write({ 'move_amount': move_amount if move_amount > 0.0 else 0.0,
						'move_travel_days': move_amount if move_amount > 0.0 else 0.0,
						'move_monthly': move_monthly,
#						'move_percent': move_percent,
						})
			######### ------- RESULTADOS FINALES DE GASTOS VARIABLES ------- #########

			amount_daily_variable = move_amount + operator_salary + total_highway_toll + factor_mtto_travel_days + factor_tires_travel_days + diesel_travel_days
			amount_travel_days_variable = amount_daily_variable / rec.days
#			amount_percentage_variable = (amount_daily_variable / rec.total_ingr)*100

			rec.write({ 'amount_daily_variable': amount_travel_days_variable if amount_travel_days_variable > 0.0 else 0.0,
						'amount_travel_days_variable':  amount_daily_variable if amount_daily_variable > 0.0 else 0.0,
#						'amount_percentage_variable': amount_percentage_variable,
						})



			############ ---------- GASTOS ADMINISTRATIVOS --------------- ###########
			amount_acumulated_administrative = 0.0
			amount_monthly_administrative = 0.0
			amount_daily_administrative = 0.0
			amount_travel_days_administrative = 0.0
#			amount_percentage_administrative = 0.0

			for administrative in rec.administrative_expenses_ids:
				amount_acumulated_administrative += administrative.acumulated_moth
				amount_monthly_administrative += administrative.average_moth
				amount_daily_administrative += administrative.daily_average
				travel_days = administrative.daily_average * rec.days
				administrative.write({'travel_days':travel_days})
				amount_travel_days_administrative += travel_days

			rec.write({
						'amount_acumulated_administrative': amount_acumulated_administrative ,
						'amount_monthly_administrative': amount_monthly_administrative,
						'amount_daily_administrative': amount_daily_administrative,
						'amount_travel_days_administrative': amount_travel_days_administrative,
#						'amount_percentage_administrative': amount_percentage_administrative,
				})


			############ --------- RESUMEN DE TODOS LOS CALCULOS ---------- ##############

			summary_income_monthly = total_income / rec.days
			summary_income_travel_days = total_income
			summary_income_percent = 100

			if summary_income_travel_days <= 0.0:
				raise osv.except_osv(
			                        _('Error al Calcular !'),
			                        _('No se tienen Capturadas Rutas para la Cotizacion'))
				
			summary_expenditures_travel_days = total_acumulated_days + amount_daily_variable + amount_travel_days_administrative + rec.total_security
			summary_expenditures_monthly = summary_expenditures_travel_days / rec.days
			summary_expenditures_percent = ( summary_expenditures_travel_days / summary_income_travel_days ) * 100

			summary_utility_travel_days = summary_income_travel_days - summary_expenditures_travel_days
			summary_utility_monthly = summary_utility_travel_days / rec.days
			summary_utility_percent = ( summary_utility_travel_days / summary_income_travel_days ) * 100


			#### KMS Productivos
			km_pro = 0.0
			for pro in rec.route_ids:
				if pro.uncharged == False or pro.product_weight > 0.0:
					km_pro += pro.kms

			summary_km_productive_travel_days = summary_income_travel_days / km_pro
			summary_km_productive_monthly = summary_km_productive_travel_days / rec.days
			summary_km_productive_percent = ( summary_km_productive_travel_days / summary_income_travel_days ) *100

			summary_mk_shot_travel_days = summary_income_travel_days / total_kms
			summary_mk_shot_monthly = summary_mk_shot_travel_days / rec.days
			summary_mk_shot_percent = ( summary_mk_shot_travel_days / summary_income_travel_days ) * 100

			summary_cost_km_travel_days = summary_expenditures_travel_days / total_kms
			summary_cost_km_monthly = summary_cost_km_travel_days / rec.days
			summary_cost_km_percent = ( summary_cost_km_travel_days / summary_income_travel_days ) * 100

			summary_utility_km_travel_days = summary_utility_travel_days / total_kms
			summary_utility_km_monthly = summary_utility_km_travel_days / rec.days			
			summary_utility_km_percent = ( summary_utility_km_travel_days / summary_income_travel_days ) * 100


			######## Terminar el Margen Operativo
			
			summary_margin_travel_days = summary_income_travel_days - diesel_travel_days - operator_salary - total_highway_toll - move_amount - rec.total_security ### AGREGAMOS EL COSTO DE SEGURO VERIFICAR
			summary_margin_monthly = summary_margin_travel_days / rec.days
			summary_margin_percent = (summary_margin_travel_days / summary_income_travel_days ) * 100

			rec.write({
						'summary_income_monthly': summary_income_monthly,
						'summary_income_travel_days': summary_income_travel_days,
						'summary_income_percent': summary_income_percent,

						'summary_expenditures_travel_days': summary_expenditures_travel_days,
						'summary_expenditures_monthly': summary_expenditures_monthly,
						'summary_expenditures_percent': summary_expenditures_percent ,

						'summary_utility_monthly': summary_utility_monthly,
						'summary_utility_travel_days': summary_utility_travel_days,
						'summary_utility_percent': summary_utility_percent,

						'summary_km_productive_monthly': summary_km_productive_monthly,
						'summary_km_productive_travel_days': summary_km_productive_travel_days,
						'summary_km_productive_percent': summary_km_productive_percent,

						'summary_mk_shot_monthly': summary_mk_shot_monthly,
						'summary_mk_shot_travel_days': summary_mk_shot_travel_days,
						'summary_mk_shot_percent': summary_mk_shot_percent,

						'summary_cost_km_monthly': summary_cost_km_monthly,
						'summary_cost_km_travel_days': summary_cost_km_travel_days,
						'summary_cost_km_percent': summary_cost_km_percent,

						'summary_utility_km_monthly': summary_utility_km_monthly,
						'summary_utility_km_travel_days': summary_utility_km_travel_days,
						'summary_utility_km_percent': summary_utility_km_percent,

						'summary_margin_monthly': summary_margin_monthly,
						'summary_margin_travel_days': summary_margin_travel_days,
						'summary_margin_percent': summary_margin_percent,
				})

			######## ------------- CALCULAS LOS PORCENTAJES CORRESPONDIENTES DE GASTOS SE HACEN AL FINAL AL OBTENER EL MONTO TOTAL DE GASTOS SE PUEDE DIVIDIR CADA CANTIDAD INDIVIDUAL ENTRE ESTE MONTO * 100 ---- ######


		return True


	def onchange_operating_cost_products(self, cr, uid, ids, load_operating_cost):
		if load_operating_cost == False:
			return {}

		################### ------ COSTOS FIJOS OPERATIVOS ---------- ################
		### Creando los Costos Fijos Operativos
		product_obj = self.pool.get('product.product')
		product_fixes_ids = product_obj.search(cr, uid, [('tms_category', '=', 'indirect_expense'), ('active', '=', True), ('operating_fixed_cost', '=', True)])
		fixes_list = []

		date_start = ''
		date_end = ''
		number_months = 0
		fiscalyear_id = 0
		fiscalyear_obj = self.pool.get('account.fiscalyear')
			
		if product_fixes_ids:
			read = product_obj.read(cr, uid, product_fixes_ids[0])
			read_name = product_obj.read(cr, uid, product_fixes_ids[0])['name']

			date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			date_strp = datetime.strptime(date_now, '%Y-%m-%d %H:%M:%S')
			year = date_strp.year
			month = date_strp.month
			day = date_strp.day

			#date_revision = date_strp - timedelta(days=30)

			if day == 15 and month == 01:
				year_asign = year - 1
				cadena_date = '0101'+str(year-1)
				date_start = datetime.strptime(cadena_date, "%d%m%Y") # Al realizar o crear mi propia fecha ya es del tipo strp para realizar calculos con fechas timedelta
				cadena_date_02 = '0101'+str(year)
				date_end = datetime.strptime(cadena_date_02, "%d%m%Y")
				cadena_closed = '3112'+str(year-1)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				number_months = 12

			elif day < 15 and month == 01:
				year_asign = year - 1
				cadena_date = '0111'+str(year_asign)
				date_start = datetime.strptime(cadena_date, "%d%m%Y") 
				cadena_date_02 = '0112'+str(year_asign)
				date_end = datetime.strptime(cadena_date_02, "%d%m%Y")

				cadena_closed = '3112'+str(year-1)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				number_months = 11

			elif day < 15 and month == 02:
				year_asign = year - 1
				cadena_date = '0112'+str(year_asign)
				date_start = datetime.strptime(cadena_date, "%d%m%Y") 
				cadena_date_02 = '0101'+str(year)
				date_end = datetime.strptime(cadena_date_02, "%d%m%Y")

				cadena_closed = '3112'+str(year-1)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				number_months = 12

			elif day ==15 and month == 02:
				cadena_date = '0101'+str(year)
				date_start = datetime.strptime(cadena_date, "%d%m%Y") # Al realizar o crear mi propia fecha ya es del tipo strp para realizar calculos con fechas timedelta
				cadena_date_02 = '0102'+str(year)
				date_end = datetime.strptime(cadena_date_02, "%d%m%Y")

				cadena_closed = '3112'+str(year)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				number_months = 1


			else:
				cadena_closed = '3112'+str(year)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				if day < 15:
					ms = month - 2
					if ms < 10:
						month_asign ='0' + str(ms)
					else:
						month_asign = str(ms)
					cadena_date = '01'+month_asign+str(year)
					date_start = datetime.strptime(cadena_date, "%d%m%Y")
					ms_02 = month -1 
					if ms_02 < 10:
						month_asign_02 ='0' + str(ms_02)
					else:
						month_asign_02 = str(ms_02)
					cadena_date_02 = '01'+month_asign_02+str(year)
					date_end = datetime.strptime(cadena_date_02, "%d%m%Y")
					number_months = month - 2 

				elif day == 15:
					ms = month - 1
					if ms < 10:
						month_asign ='0' + str(ms)
					else:
						month_asign = str(ms)
					cadena_date = '01'+month_asign+str(year)
					date_start = datetime.strptime(cadena_date, "%d%m%Y")
					ms_02 = month
					if ms_02 < 10:
						month_asign_02 ='0' + str(ms_02)
					else:
						month_asign_02 = str(ms_02)
					cadena_date_02 = '01'+month_asign_02+str(year)
					date_end = datetime.strptime(cadena_date_02, "%d%m%Y")
					number_months = month - 1

				elif day > 15:
					ms = month - 1
					if ms < 10:
						month_asign ='0' + str(ms)
					else:
						month_asign = str(ms)
					cadena_date = '01'+month_asign+str(year)
					date_start = datetime.strptime(cadena_date, "%d%m%Y")
					ms_02 = month
					if ms_02 < 10:
						month_asign_02 ='0' + str(ms_02)
					else:
						month_asign_02 = str(ms_02)
					cadena_date_02 = '15'+month_asign_02+str(year)
					date_end = datetime.strptime(cadena_date_02, "%d%m%Y")
					number_months = month - 1


			for product in product_obj.browse(cr, uid, product_fixes_ids):
				account_list = []
				for ac in product.tms_account_ids:
					account_list.append(ac.id)


				# account_period_obj = self.pool.get('account.period')
				# account_period_ids = account_period_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear_id),('date_stop','<',date_end)])
				# number_periods = len(account_period_ids)
				############ HACER EL QUERY PARA EL RESULTADO DE TODOS LOS ACCOUNT MOVE LINE QUE RESULTEN COMPARAR Y DE AHI TOMAR LA INFORMACION PARA LO QUE SE NECESITE
				############ NO HACER POR PYTHON SI NO POR SQL DEBIT - CREDIT

				############# EMPEZAMOS EL QUERY PARA TRAER TODOS LOS MOVIEMIENTOS DE ACCOUNT_MOVE_LINE DE LAS CUENTAS DE LOS PRODUCTOS #############

				cumulative_sum = 0.0

				for account in account_list:
					cr.execute("""
						select sum(coalesce(debit) - coalesce(credit)) from account_move_line
						where
						period_id in (select id from account_period where fiscalyear_id = %s and date_stop < %s)
						and account_id = %s""", (fiscalyear_id, date_end, account))
					suma = cr.fetchall()
					suma01 = suma[0][0]

					if suma01:
						cumulative_sum += suma01
					# else:
					# 	suma01 = 0.0
					# 	cumulative_sum += cumulative_sum
				average_moth = cumulative_sum / number_months
				daily_average = average_moth / 30

				### Aqui buscamos dentro de las cuentas que tenga cada producto el debit - credit para al final crear un diccionario para crear las lineas
				# Debemos buscar los montos de acuerdo a la fecha actual de la fecha inicio del periodo contable
				xline = (0 ,0,{
								'product_id': product.id,
								'name': product.name,
								'acumulated_moth': cumulative_sum, # Calculados en base a los resultados de la busqueda
								'average_moth': average_moth if cumulative_sum else 0.00, # Calculados en base a los resultados de la busqueda
								'daily_average': daily_average if average_moth else 0.00, # Calculados en base a los resultados de la busqueda
								'travel_days': 0.0, # Calculados en base a los resultados de la busqueda
								#'percent': 0.0, # Calculados en base a los resultados de la busqueda
						})
				fixes_list.append(xline)
			return {'value' : {'operating_cost_ids' : [x for x in fixes_list]}}
		else:
			warning = {}
			title =  _("Error de Configuracion!")
			message = "No se Encontraron productos definidos como Gastos Fijos de Operacion"
			warning = {
					'title': title,
					'message': message,
			}
			
			warning['message'] = message 
			return {'warning':warning}


	def onchange_administrative_expenses(self, cr, uid, ids, load_administrative_expenses):

		if load_administrative_expenses == False:
			return {}

		################### ------ GASTOS ADMINISTRATIVOS ---------- ################
		### CREANDO LOS GASTOS ADMINISTRATIVOS
		product_obj = self.pool.get('product.product')
		product_administrative_ids = product_obj.search(cr, uid, [('tms_category', '=', 'indirect_expense'), ('active', '=', True), ('administrative_expense', '=', True)])
		administrative_list = []
		date_start = ''
		date_end = ''
		number_months = 0
		fiscalyear_id = 0
		fiscalyear_obj = self.pool.get('account.fiscalyear')

		if product_administrative_ids:
			read = product_obj.read(cr, uid, product_administrative_ids[0])
			read_name = product_obj.read(cr, uid, product_administrative_ids[0])['name']
			date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			date_strp = datetime.strptime(date_now, '%Y-%m-%d %H:%M:%S')
			year = date_strp.year
			month = date_strp.month
			day = date_strp.day

			#date_revision = date_strp - timedelta(days=30)

			if day == 15 and month == 01:
				year_asign = year - 1
				cadena_date = '0101'+str(year-1)
				date_start = datetime.strptime(cadena_date, "%d%m%Y") # Al realizar o crear mi propia fecha ya es del tipo strp para realizar calculos con fechas timedelta
				cadena_date_02 = '0101'+str(year)
				date_end = datetime.strptime(cadena_date_02, "%d%m%Y")
				cadena_closed = '3112'+str(year-1)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				number_months = 12

			elif day < 15 and month == 01:
				year_asign = year - 1
				cadena_date = '0111'+str(year_asign)
				date_start = datetime.strptime(cadena_date, "%d%m%Y") 
				cadena_date_02 = '0112'+str(year_asign)
				date_end = datetime.strptime(cadena_date_02, "%d%m%Y")

				cadena_closed = '3112'+str(year-1)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				number_months = 11

			elif day < 15 and month == 02:
				year_asign = year - 1
				cadena_date = '0112'+str(year_asign)
				date_start = datetime.strptime(cadena_date, "%d%m%Y") 
				cadena_date_02 = '0101'+str(year)
				date_end = datetime.strptime(cadena_date_02, "%d%m%Y")

				cadena_closed = '3112'+str(year-1)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				number_months = 12

			elif day ==15 and month == 02:
				cadena_date = '0101'+str(year)
				date_start = datetime.strptime(cadena_date, "%d%m%Y") # Al realizar o crear mi propia fecha ya es del tipo strp para realizar calculos con fechas timedelta
				cadena_date_02 = '0102'+str(year)
				date_end = datetime.strptime(cadena_date_02, "%d%m%Y")

				cadena_closed = '3112'+str(year)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				number_months = 1


			else:
				cadena_closed = '3112'+str(year)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				if day < 15:
					ms = month - 2
					if ms < 10:
						month_asign ='0' + str(ms)
					else:
						month_asign = str(ms)
					cadena_date = '01'+month_asign+str(year)
					date_start = datetime.strptime(cadena_date, "%d%m%Y")
					ms_02 = month -1 
					if ms_02 < 10:
						month_asign_02 ='0' + str(ms_02)
					else:
						month_asign_02 = str(ms_02)
					cadena_date_02 = '01'+month_asign_02+str(year)
					date_end = datetime.strptime(cadena_date_02, "%d%m%Y")

					number_months = month - 2 

				elif day == 15:
					ms = month - 1
					if ms < 10:
						month_asign ='0' + str(ms)
					else:
						month_asign = str(ms)
					cadena_date = '01'+month_asign+str(year)
					date_start = datetime.strptime(cadena_date, "%d%m%Y")
					ms_02 = month
					if ms_02 < 10:
						month_asign_02 ='0' + str(ms_02)
					else:
						month_asign_02 = str(ms_02)
					cadena_date_02 = '01'+month_asign_02+str(year)
					date_end = datetime.strptime(cadena_date_02, "%d%m%Y")
					number_months = month - 1

				elif day > 15:
					ms = month - 1
					if ms < 10:
						month_asign ='0' + str(ms)
					else:
						month_asign = str(ms)
					cadena_date = '01'+month_asign+str(year)
					date_start = datetime.strptime(cadena_date, "%d%m%Y")
					ms_02 = month
					if ms_02 < 10:
						month_asign_02 ='0' + str(ms_02)
					else:
						month_asign_02 = str(ms_02)
					cadena_date_02 = '15'+month_asign_02+str(year)
					date_end = datetime.strptime(cadena_date_02, "%d%m%Y")
					number_months = month - 1


			for product in product_obj.browse(cr, uid, product_administrative_ids):
				account_ids = product.tms_account_ids
				account_list = []
				for ac in product.tms_account_ids:
					account_list.append(ac.id)
				############# EMPEZAMOS EL QUERY PARA TRAER TODOS LOS MOVIEMIENTOS DE ACCOUNT_MOVE_LINE DE LAS CUENTAS DE LOS PRODUCTOS #############

				cumulative_sum = 0.0

				for account in account_list:
					cr.execute("""
						select sum(coalesce(debit) - coalesce(credit)) from account_move_line
						where
						period_id in (select id from account_period where fiscalyear_id = %s and date_stop < %s)
						and account_id = %s""", (fiscalyear_id, date_end, account))
					suma = cr.fetchall()
					suma01 = suma[0][0]

					if suma01:
						cumulative_sum += suma01
					# else:
					# 	suma01 = 0.0
					# 	cumulative_sum += cumulative_sum
				average_moth = cumulative_sum / number_months
				daily_average = average_moth / 30

				### Aqui buscamos dentro de las cuentas que tenga cada producto el debit - credit para al final crear un diccionario para crear las lineas
				# Debemos buscar los montos de acuerdo a la fecha actual de la fecha inicio del periodo contable
				xline = (0 ,0,{
								'product_id': product.id,
								'name': product.name,
								'acumulated_moth': cumulative_sum,  # Calculados en base a los resultados de la busqueda
								'average_moth':  average_moth if cumulative_sum else 0.00, # Calculados en base a los resultados de la busqueda
								'daily_average': daily_average if average_moth else 0.00, # Calculados en base a los resultados de la busqueda
								'travel_days': 0.0, # Calculados en base a los resultados de la busqueda
								#'percent': 0.0, # Calculados en base a los resultados de la busqueda
						})
				administrative_list.append(xline)
			return {'value' : {'administrative_expenses_ids' : [x for x in administrative_list]}}
		else:
			warning = {}
			title =  _("Error de Configuracion!")
			message = "No se Encontraron productos definidos como Gastos Administrativos"
			warning = {
					'title': title,
					'message': message,
			}
			
			warning['message'] = message 
			return {'warning':warning}


	def onchange_quotation(self, cr, uid, ids, parameter_id, days):
#		if not parameter_id:
#			return {'value': {
#							  #'pricelist_id': False,
#							  #'currency_id': False,}
#					}
		parameter_obj = self.pool.get('tms.quotation.config')
		parameter_browse = parameter_obj.browse(cr, uid, [parameter_id], context=None)[0]
		val = {
				'month_travel': parameter_browse.month_days / days,
				'diesel_cost' : parameter_browse.diesel_cost,
				'performance_loaded' : parameter_browse.charged_performance,
				'uncharged_performance' : parameter_browse.uncharged_performance,
				'factor_mtto' : parameter_browse.factor_mtto,
				'factor_tires' :parameter_browse.factor_tires, 
		#'pricelist_id': pricelist,
		#'currency_id': currency,
		}
		return {'value': val}

#	_order = "id desc"


	def copy(self, cr, uid, id, default=None, context=None):
		quotation = self.browse(cr, uid, id, context=context)
		if not default:
			default = {}
		default.update({
						
						#'unit_ids'	  : False, 
						'state'		 : 'draft',
						'agreement_id'	: False, 
						
						})
		return super(tms_quotation, self).copy(cr, uid, id, default, context=context)

	def action_confirmed(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids,{'state':'confirmed'})
		self.action_calculate(cr, uid, ids, context=None)
		for obj in self.browse(cr, uid, ids, context=context):
			self.message_post(cr, uid, [obj.id], body=_("Quotation %s <em>%s</em> <b>confirmed</b>.") % (obj.sequence,obj.name),  context=context)
		return True


	def action_draft(self, cr,uid,ids,context={}):
		self.write(cr, uid, ids, {'state':'draft'})
		for obj in self.browse(cr, uid, ids, context=context):
			self.message_post(cr, uid, [obj.id], body=_("Quotation %s <em>%s</em> <b>drafted </b>.") % (obj.sequence,obj.name) ,context=context)
		return True


	def action_done(self,cr,uid,ids,context={}): 
		for rec in self.browse(cr, uid, ids, context=context):
			self.message_post(cr, uid, [rec.id], body=_("Quotation %s <em>%s</em> <b>done</b>.") % (rec.sequence,rec.name),  context=context)
		self.write(cr, uid, ids, {'state':'done'})		
		return True	


	def action_cancel(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'cancel'})
		tms_agreement_obj = self.pool.get('tms.agreement')
		for obj in self.browse(cr, uid, ids, context=context):
			self.message_post(cr, uid, [obj.id], body=_("Quotation %s <em>%s</em> <b>cancelled</b>.") % (obj.sequence,obj.name),  context=context)
		for quotation in self.browse(cr, uid, ids, context=context):
			if quotation.agreement_id:
				self.message_post(cr, uid, [quotation.id], body=_("Agreement <em>%s</em> <b>has been Eliminated</b>.") % (quotation.agreement_id.name),  context=context)
				#tms_agreement_obj.unlink(cr, uid, [quotation.agreement_id.id], context=None)
				tms_agreement_obj.write(cr, uid, [quotation.agreement_id.id], {'state':'cancel'})
				quotation.write({'agreement_id':False})
		return True

	def _check_mark(self, cr, uid, ids, context=None):
		for rec in self.browse(cr,uid,ids):
			i=0
			for route in rec.route_ids:
				if route.mark == True:
					i += 1
			if i <= 1:
				return True
		return False

	# def _check_factor(self, cr, uid, ids, context=None):
	# 	for rec in self.browse(cr,uid,ids):
	# 		i=0
	# 		for factor in rec.factor_ids:
	# 			if factor:
	# 				i += 1
	# 		if i <= 1:
	# 			return True
	# 	return False

	# _constraints = [
	# 	(_check_mark, 'Error ! No se pueden tener 2 Rutas Marcadas ', ['Rutas']), (_check_factor, 'Error ! No se puede calcular mas de 1 factor por Cotizacion ', ['Factores'])
	# ]
	_constraints = [
		(_check_mark, 'Error ! No se pueden tener 2 Rutas Marcadas ', ['Rutas'])]
tms_quotation()

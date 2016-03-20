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


#################### WIZARD PARA GENERAR EL AGREEMENT

class tms_quotation_agreement_wizard(osv.osv_memory):
	_name = 'tms.quotation.agreement.wizard'
	_description = 'Make Travel from Agreement'

	def _get_selection(self, cr, uid, context=None):
		active_id = context and context.get('active_id', False)
		print "######################### ACTIVE IDDDDDDDDDDD", active_id
		tms_quotation_obj = self.pool.get('tms.quotation')
		route_list = []
		for quotation in tms_quotation_obj.browse(cr, uid, [active_id], context=context):
			if not quotation.route_ids:
				return ()
			for route in quotation.route_ids:
				route_list.append((route.route_id.id,route.route_id.name))
		return (tuple(route_list))

	def _get_selection_2(self, cr, uid, context=None):
		active_id = context and context.get('active_id', False)
		print "######################### ACTIVE IDDDDDDDDDDD", active_id
		tms_quotation_obj = self.pool.get('tms.quotation')
		route_list = []
		for quotation in tms_quotation_obj.browse(cr, uid, [active_id], context=context):
			if not quotation.route_ids:
				return ()
			for route in quotation.route_ids:
				route_list.append((route.route_id.id,route.route_id.name))
		return (tuple(route_list))

	_columns = {

		'shop_id': fields.many2one('sale.shop', 'Shop', required=True, readonly=False),
		'date': fields.date('Date Start', required=True),
		'partner_id': fields.many2one('res.partner', 'Customer', required=False, select=True, readonly=False),
		'partner_invoice_id': fields.many2one('res.partner', 'Invoice Address', required=True),
		'partner_order_id': fields.many2one('res.partner', 'Ordering Contact', required=True),
		'departure_address_id': fields.many2one('res.partner', 'Departure Address', required=True),
		'arrival_address_id': fields.many2one('res.partner', 'Arrival Address', required=True),
		'upload_point': fields.char('Upload Point', size=128, readonly=False, required=True),
		'download_point': fields.char('Download Point', size=128, required=True, ),
		'date_start': openerp.osv.fields.date('Date Star', required=True),
		'date_end': openerp.osv.fields.date('Date End', required=True),
		'currency_id': fields.many2one('res.currency','Currency'),
		'quotation_id': fields.many2one('tms.quotation', 'Active ID'),
		'route_seleccion': fields.selection(_get_selection, 'Selecciona la Ruta de Partida'),
		'route_seleccion_return': fields.selection(_get_selection_2, 'Selecciona la Ruta de Partida'),

	}

	def _get_active_shop(self,cr,uid,context=None): # esta funcion en el wizard le va agregar por defecto la session en la que estamos
		res_obj = self.pool.get('res.users')
		res = res_obj.browse(cr, uid, uid, context=context)
		print "################################################# RES USERS", res.company_id.name
		shop_obj = self.pool.get('sale.shop')
		shop = shop_obj.search(cr, uid, [('company_id','=',res.company_id.id)], limit=1)
		# shop_id = shop[0]
		# print "#######################################################  SHOP [0]", shop_id
		if not shop:
			return None
		# return shop_id
		return shop[0]

	def _get_active_customer(self,cr,uid,context=None): # esta funcion en el wizard le va agregar por defecto la session en la que estamos
		active_id = context and context.get('active_id', False)
		print "######################### ACTIVE IDDDDDDDDDDD", active_id
		tms_quotation_obj = self.pool.get('tms.quotation')
		partner_id = []
		for customer in tms_quotation_obj.browse(cr, uid, [active_id], context=context):
			if customer.partner_id:
				partner_id.append(customer.partner_id.id)

		return partner_id[0]

	def _get_active_id(self,cr,uid,context=None): # esta funcion en el wizard le va agregar por defecto la session en la que estamos
		active_id = context and context.get('active_id', False)
		if not active_id:
			return []

		return active_id

	_defaults = {
		'shop_id': _get_active_shop,
		'partner_id': _get_active_customer,
		'date': lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
		'date_start': lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
		'currency_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.currency_id.id,
		'quotation_id': _get_active_id,

	}

	def onchange_partner_id(self, cr, uid, ids, partner_id):
		if not partner_id:
			return {'value': {'partner_invoice_id': False, 
							'partner_order_id': False, 
							'payment_term': False, 
							#'pricelist_id': False,
							#'currency_id': False, 
							'user_id': False}
					}
		addr = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['invoice', 'contact', 'default', 'delivery'])
		part = self.pool.get('res.partner').browse(cr, uid, partner_id)
		pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
		payment_term = part.property_payment_term and part.property_payment_term.id or False
		dedicated_salesman = part.user_id and part.user_id.id or uid
		val = {
				'partner_invoice_id': addr['invoice'] if addr['invoice'] else addr['default'],
				'partner_order_id': addr['contact'] if addr['contact'] else addr['default'],
				'payment_term': payment_term,
				'user_id': dedicated_salesman,
				#'pricelist_id': pricelist,
				#'currency_id': currency,
		}
		return {'value': val}

	def button_generate_agreement(self, cr, uid, ids, context=None):
		active_id = context and context.get('active_id', False)
		tms_quotation_obj = self.pool.get('tms.quotation')
		tms_agreement_obj = self.pool.get('tms.agreement')
		product_obj = self.pool.get('product.product')
		fpos_obj = self.pool.get('account.fiscal.position')
		product_id = product_obj.search(cr, uid, [('tms_category', '=', 'freight'),('tms_default_freight','=',True),('active','=', 1)], limit=1)

		product_browse = product_obj.browse(cr, uid, product_id, context=context)[0]
		for wizard in self.browse(cr, uid, ids, context=context):
			route_mark_id = []
			route_uncharged_id = []
			product_shipped_list = []
			agreement_line_list = []
			factor_list = []
			tms_agreement_id = 0
			expenses_list = []
			factor_driver_list = []

			if wizard.route_seleccion == wizard.route_seleccion_return:
				raise osv.except_osv(
					_('Error!'),
					_('La Ruta de Partida y Retorno no puede ser la misma seleccione una Distinta ...'))
			for quotation in tms_quotation_obj.browse(cr, uid, [active_id], context=context):
				
				for route in quotation.route_ids:
					if route.mark:
						if route.route_id.expense_driver_factor:
							product_obj = self.pool.get('product.product')
							product_id = product_obj.search(cr, uid, [('tms_category', '=', 'freight'),('tms_default_freight','=',True),('active','=', 1)], limit=1)
							if not product_id:
								raise osv.except_osv(
									_('Error, No se puede generar el Acuerdo!'),
									_('No se tiene Configurado un producto con las caracteristicas (tms_category, =, freight),(tms_default_freight,=,True),(active,=, 1)'))
							product_browse = product_obj.browse(cr, uid, product_id, context=context)[0]
							for factor in route.route_id.expense_driver_factor:
								print "########################################## FACTOR TYPE", factor.factor_type
								print "########################################## FACTOR TYPE", factor.range_start
								xline_factor = (0,0,{
										    		'name'          : product_browse.name,
											        'category'      : factor.category,
											        'factor_type'   : factor.factor_type,
											        'framework'     : factor.framework if factor.framework else False,
											        'range_start'   : factor.range_start if factor.range_start else 0.0,
											        'range_end'     : factor.range_end if factor.range_end else 0.0,
											        'factor'        : factor.factor if factor.factor else False,
											        'fixed_amount'  : factor.fixed_amount if factor.fixed_amount else 0.0,
											        'mixed'         : factor.mixed if factor.mixed else False,
											        'factor_special_id': factor.factor_special_id.id if factor.factor_special_id.id else False,
											        'variable_amount' : factor.variable_amount if factor.variable_amount else False,
											        'total_amount'  : factor.total_amount if factor.total_amount else 0.0,
											        'sequence'      : 0,
											        'notes'         : "Factor cargado de la ruta "+route.route_id.name,
											        'control'       : factor.control if factor.control == True else False,### Revisar si es necesario eliminarlo
											        'driver_helper' : factor.driver_helper if factor.driver_helper else False,

										})
								print "######################################## XLINE FACTOR", xline_factor
								print "######################################## XLINE FACTOR", xline_factor
								print "######################################## XLINE FACTOR", xline_factor
								factor_driver_list.append(xline_factor)

				control = False
				if quotation.agreement_id:
					raise osv.except_osv(
								_('Error, No se puede generar el Acuerdo!'),
								_('La Cotizacion Tiene el Acuerdo %s asignado, duplica el registro o crea uno Nuevamente ...') % (quotation.agreement_id.name))
				elif quotation.state != 'confirmed':
					raise osv.except_osv(
								_('Error, No se puede generar el Acuerdo!'),
								_('La Cotizacion %s se encuentra en el Estado Borrador, Confirmelo antes de crear el Acuerdo ...') % (quotation.sequence))
				else:
					i = 0
					for route in quotation.route_ids:
						if route.mark == True:
							route_mark_id.append(route.route_id.id)
						if route.uncharged:
							route_uncharged_id.append(route.route_id.id)
						if route.product_id:
							xline = (0 ,0,{
											'name': route.product_id.name,
											'product_id': route.product_id.id,
											'product_uom': route.product_uom.id,
											'product_uom_qty': route.product_weight,
											'notes': False,
											'sequence': i,
											})
							product_shipped_list.append(xline)
							i+=1
					######### CREANDO LOS FACTORES DESDE LAS RUTAS DE LA COTIZACION
					for factor in quotation.route_ids:
						xline_factor = (0,0,{
								    		'name'          : product_browse.name,
									        'category'      : 'customer',
									        'factor_type'   : factor.factor_type,
									        'framework'     : factor.framework if factor.framework else False,
									        'range_start'   : factor.range_start if factor.range_start else 0.0,
									        'range_end'     : factor.range_end if factor.range_end else 0.0,
									        'factor'        : factor.factor if factor.factor else False,
									        'fixed_amount'  : factor.fixed_amount if factor.fixed_amount else 0.0,
									        'mixed'         : factor.mixed if factor.mixed else False,
									        'factor_special_id': factor.factor_special_id.id if factor.factor_special_id.id else False,
									        'variable_amount' : factor.variable_amount if factor.variable_amount else False,
									        'total_amount'  : factor.total_amount if factor.total_amount else 0.0,
									        'sequence'      : 0,
									        'notes'         : quotation.name+" "+quotation.partner_id.name,
									        'control'       : control,
									        'driver_helper' : False,
 
								})
						factor_list.append(xline_factor)

					xline_agreement = (0,0,{
								'line_type': 'product',
								'name': product_browse.name,
								'sequence': 0,
								'product_id': product_browse.id,
								'price_unit': quotation.total_ingr,
								'tax_id': [(6, 0, [x.id for x in product_browse.taxes_id])],
								'product_uom_qty': 1,
								'product_uom': product_browse.uom_id.id,
								'control': control,
								})
					agreement_line_list.append(xline_agreement)
					print "#################### AGREEMENTS LINEASSSSSSSSSSSSS", agreement_line_list
					print "############################## RUTAAAAAAAAAAAAAAAAAAAASSSSSSSSSSSSSS", route_mark_id
					print "############################## RUTAAAAAAAAAAAAAAAAAAAASSSSSSSSSSSSSS", route_mark_id
					print "############################## RUTAAAAAAAAAAAAAAAAAAAASSSSSSSSSSSSSS", route_mark_id
					print "############################## RUTAAAAAAAAAAAAAAAAAAAASSSSSSSSSSSSSS", route_mark_id
					########--- CREANDO LOS GASTOS DESDE LA COTIZACION ---########
					sq = 0
					if quotation.total_security > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'insurance'),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado como Seguro'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'real_expense',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.total_security,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Insurance expense Units',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					if quotation.factor_mtto_travel_days > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'maintenance'),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado de tipo Mantenimiento'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'real_expense',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.factor_mtto_travel_days,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Expenditures for maintenance of the units',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					if quotation.factor_tires_travel_days > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'tires'),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado de tipo Llantas o Tires'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'real_expense',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.factor_tires_travel_days,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Expense using by Tires',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					if quotation.diesel_travel_days > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'fuel'),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado de tipo Combustible'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'fuel',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.diesel_travel_days,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Expenses for fuel consumption during the Trip',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					if quotation.toll_travel_days > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'highway_tolls'),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado de tipo Caseta'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'real_expense',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.toll_travel_days,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Expenses during the trip by highway tolls',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					if quotation.salary_travel_days > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'salary'),('tms_default_salary','=',True),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado de tipo Salario y Default por Defecto'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'salary',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.salary_travel_days,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Salary expenses Operator',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					if quotation.move_travel_days > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'move'),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado de tipo Move o Maniobra'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'real_expense',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.move_travel_days,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Moves Expenses',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					if quotation.operating_amount_all > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'fixed_operating'),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado de tipo Gastos Fijos Operativos'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'indirect',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.operating_amount_all,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Fixed Operating Costs',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					if quotation.administrative_amount_all > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'administrative_expense'),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado de tipo Gastos Administrativos'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'indirect',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.administrative_amount_all,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Administrative Expenses',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					# if factor_mtto_travel_days:
					# 	xline_expense = (0,0,{
					# 			'line_type': 'product',
					# 			'name': product_browse.name,
					# 			'sequence': 0,
					# 			'product_id': product_browse.id,
					# 			'price_unit': quotation.total_ingr,
					# 			'tax_id': [(6, 0, [x.id for x in product_browse.taxes_id])],
					# 			'product_uom_qty': 1,
					# 			'product_uom': product_browse.uom_id.id,
					# 			'control': control,
					# 			})
						# expenses_list.append(xline_expense)

					vals = {
							'shop_id': wizard.shop_id.id,
							'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
							'partner_id': wizard.partner_id.id,
							'partner_invoice_id': wizard.partner_invoice_id.id,
							'partner_order_id': wizard.partner_order_id.id,
							'departure_address_id': wizard.departure_address_id.id,
							'arrival_address_id': wizard.arrival_address_id.id,
							'upload_point': wizard.upload_point,
							'download_point': wizard.download_point,
							'date_start': wizard.date_start,
							'date_end': wizard.date_end,
							'quotation_id': active_id,
							'unit_ids': quotation.unit_ids.id,
							'unit_a': quotation.parameter_id.units_number,
							'route_id': route_mark_id[0] if route_mark_id else False,
							'route_return_id': route_uncharged_id[0] if route_uncharged_id else False,
							'agreement_shipped_product': [x for x in product_shipped_list],
							'agreement_line': [x for x in agreement_line_list] if product_id else [],
							'units_a': quotation.parameter_id.units_number,
							'agreement_customer_factor': [x for x in factor_list] if factor_list else [],
							'agreement_driver_factor': [x for x in factor_driver_list] if factor_driver_list else [],
							'agreement_direct_expense_line': [x for x in expenses_list] if expenses_list else False,
							'state': 'confirmed',
							'departure': True if int(wizard.route_seleccion) == route_mark_id[0] else False,
							'departure_2': True if int(wizard.route_seleccion) == route_uncharged_id[0] else False,
							'arrival': True if int(wizard.route_seleccion_return) == route_mark_id[0] else False,
							'arrival_2': True if int(wizard.route_seleccion_return) == route_uncharged_id[0] else False,

							}
	
					print "################################################### VALORES PARA CREAR EL ACUERDOOOOOOOOOOOO", vals
					tms_agreement_id = tms_agreement_obj.create(cr, uid, vals, context)
					if tms_agreement_id:
						quotation.write({'agreement_id': tms_agreement_id})
					for agr in tms_agreement_obj.browse(cr, uid, [tms_agreement_id], context=context):
						agr.action_mount_write()

		return {
			'type': 'ir.actions.act_window',
			'name': _('TMS AGREEMENTS'),
			'res_model': 'tms.agreement',
			'res_id': tms_agreement_id,
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': False,
			'target': 'current',
			'nodestroy': True,
		}
tms_quotation_agreement_wizard()
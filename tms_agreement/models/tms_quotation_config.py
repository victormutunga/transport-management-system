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


class tms_quotation_config(osv.Model):
	_name = 'tms.quotation.config'
	_description = 'Parameters for TMS QUOTATION'

	_columns = {
		'name': fields.char('Description', size=128, required=False),
		'month_days': fields.float('Days of the Month', digits=(9,2), required=True),
		'diesel_cost': fields.float('Cost of Diesel', digits=(9,2), required=True),
		'units_number': fields.float('Units Number', digits=(9,0), required=True),
		'number_trailers': fields.float('Number of Trailers', digits=(4,0), required=True),
		'operators': fields.float('Operators', digits=(4,0), required=True),
		'movers': fields.float('Movers', digits=(4,0), required=True),
		'tires': fields.float('Number of Tires', digits=(4,0), required=True),
		'charged_performance': fields.float('Charged Performance', digits=(9,2), required=True),
		'uncharged_performance': fields.float('Uncharged Performance', digits=(9,2), required=True),
		'salary_diary_movers': fields.float('Salary Movers Journal', digits=(9,2), required=True),
		'integrated_wage_factor': fields.float('Integrated Wage Factor', digits=(9,2), required=True),
		'insurance_satellite_equipment': fields.float('Insurance Satellite Equipment', digits=(9,2), required=True),
		'tractor_insurance': fields.float('Tractor Insurance', digits=(9,2), required=True),
		'trailer_insurance': fields.float('Trailer Insurance', digits=(9,2), required=True),
		'dolly_insurance': fields.float('Dolly Insurance', digits=(9,2), required=True),
		'ambiental_insurance': fields.float('Ambiental Insurance', digits=(9,2), required=True),
		'factor_administrative_expenses': fields.float('Factor Administrative Expenses', digits=(9,2), required=True),
		'factor_mtto': fields.float('Maintenance Factor', digits=(9,2), required=True),
		'factor_tires': fields.float('Tires Factor', digits=(9,2), required=True),

	}
	_defaults = {
	'month_days': 30,
	'name': 'Parameters',
	}

	def _check_unique(self, cr, uid, ids, context=None):
		if not ids:
			return True
		tms_quotation_config_obj = self.pool.get('tms.quotation.config')
		tms_quotation_config_ids = tms_quotation_config_obj.search(cr, uid, [('id','!=',ids[0])])
		if tms_quotation_config_ids:
			return False		   
		return True


	_constraints = [
		(_check_unique, 'Error ! Should only be kept of parameters', ['id'])
	]
tms_quotation_config()
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


class tms_administrative_cost(osv.Model):
	_name = 'tms.administrative.cost'
	_description = 'Fixed Operating Costs'

	_columns = {
		'product_id': fields.many2one('product.product','Product'),
		'name': fields.char('Concept', size=128, required=False),
		'product_id': fields.char('Concep', size=128, required=False),
		'acumulated_moth': fields.float('Accumulated current month', digits=(12,4)),
		'average_moth': fields.float('Average Month', digits=(12,4)),
		'daily_average': fields.float('Daily Average', digits=(12,4)),
		'travel_days': fields.float('Travel Days', digits=(12,4)),
		'percent': fields.float('%', digits=(2, 2), required=False),
		'quotation_id': fields.many2one('tms.quotation', 'Quotation ID', ondelete='cascade'),			  

	}
	_defaults = {

	}
	_order = "acumulated_moth desc"
tms_administrative_cost()

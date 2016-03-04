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
from datetime import datetime, date, timedelta
from osv.orm import browse_record, browse_null
from osv.orm import except_orm
from tools.translate import _
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import decimal_precision as dp
import netsvc
import openerp


class fleet_vehicle_mro_program_reschedule_line(osv.osv_memory):
    _name ='fleet.vehicle.mro_program.re_schedule.line'
    _description = 'Vehicle MRO Program re-schedule line'
    _columns = {
        'wizard_id'                 : fields.many2one('fleet.vehicle.mro_program.re_schedule', string="Wizard", ondelete='CASCADE'),
        'vehicle_id'                : fields.many2one('fleet.vehicle', 'Vehicle', required=True, readonly=True),
        'mro_program_id'            : fields.related('vehicle_id', 'mro_program_id', type='many2one', relation='product.product', string='Maintenance Program', readonly=True),
        'cycle_next_service'        : fields.related('vehicle_id', 'cycle_next_service', type='many2one', relation='product.product', string='Next Maintenance Service', readonly=True),
        'sequence_next_service'     : fields.related('vehicle_id', 'sequence_next_service', string='Cycle Seq. Next Serv.', readonly=True),
        'odometer'                  : fields.related('vehicle_id', 'odometer', string='Accumulated Odometer', readonly=True),
        'current_odometer'          : fields.related('vehicle_id', 'current_odometer_read', string='Current Odometer', readonly=True),
        'avg_odometer_uom_per_day'  : fields.related('vehicle_id', 'avg_odometer_uom_per_day', string='Avg Distance/Time per day', readonly=True),
        'date_next_service'         : fields.related('vehicle_id', 'date_next_service', type='date', string='Date Next Serv.', readonly=True),
        'next_date'                 : fields.date('NEW Next Service', required=True),
        }

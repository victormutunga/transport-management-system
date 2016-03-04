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


class fleet_vehicle_mro_program_reschedule(osv.osv_memory):
    _name ='fleet.vehicle.mro_program.re_schedule'
    _description = 'Vehicle MRO Program re-schedule on avg distance/time per day'

    _columns = {
        'control'     : fields.boolean('Control'),
        'vehicle_ids' : fields.one2many('fleet.vehicle.mro_program.re_schedule.line', 'wizard_id', 'Vehicles'),
        }
    
    def do_re_schedule(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            vehicle_obj = self.pool.get('fleet.vehicle')
            for vehicle in rec.vehicle_ids:
                vehicle_obj.write(cr, uid, [vehicle.vehicle_id.id], {'date_next_service':vehicle.next_date})
                
        return {'type': 'ir.actions.act_window_close'}
    
    
    def _get_vehicle_ids(self, cr, uid, context=None):
        vehicle_ids = []
        ids = context.get('active_ids', False)
        if ids:
            vehicle_obj = self.pool.get('fleet.vehicle')
            for rec in vehicle_obj.browse(cr, uid, ids):
                vehicle_ids.append({'vehicle_id'        : rec.id,
                                    'mro_program_id'    : rec.mro_program_id.id,
                                    'cycle_next_service': rec.cycle_next_service.id,
                                    'sequence_next_service': rec.sequence_next_service,
                                    'odometer'          : rec.odometer,
                                    'current_odometer'  : rec.current_odometer_read,
                                    'avg_odometer_uom_per_day'  : rec.avg_odometer_uom_per_day,
                                    'date_next_service' : rec.date_next_service,
                                    'next_date'         : vehicle_obj.get_next_service_date(cr, uid, [rec.id]), 
                                    })

        return vehicle_ids
    
    _defaults = {
            'vehicle_ids'   : _get_vehicle_ids,
            'control'       : False,
             }

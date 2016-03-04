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

    
class fleet_vehicle_mro_program(osv.Model):
    _name = 'fleet.vehicle.mro_program'
    _description = 'Fleet Vehicle MRO Program'

    _columns = {
        'vehicle_id'     : fields.many2one('fleet.vehicle', 'Vehicle', required=True, ondelete='restrict'),
        'mro_cycle_id'   : fields.many2one('product.product', 'MRO Cycle', required=True, ondelete='restrict'),
        'trigger'        : fields.integer('Scheduled at', required=True),
        'sequence'       : fields.integer('Sequence', required=True),
        'mro_service_order_id'       : fields.many2one('tms.maintenance.order', 'MRO Service Order', ondelete='restrict'),
        'mro_service_order_date'     : fields.related('mro_service_order_id', 'date', type='datetime', string="Date", store=True, readonly=True),
        'mro_service_order_distance' : fields.related('mro_service_order_id', 'accumulated_odometer', type='float', string="mi/km", store=True, readonly=True),
        'next_date'     : fields.date('Date Next Service'),
        'diference' : fields.integer('Distance in between'),
        }

    _defaults = {
        'next_date'      : lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT),
        'diference' : lambda *a: 0,
        }

    _order = 'trigger,sequence'

    def button_set_next_cycle_service(self, cr, uid, ids, context=None):
        #print "context: ", context
        if not ids:
            return False
        ##print "ids: ", ids
        for program_line in self.browse(cr, uid, ids):
            ##print "program_line.mro_cycle_id: ", program_line.mro_cycle_id
            ##print "program_line.sequence: ", program_line.sequence
            ##print "program_line.vehicle_id.odometer: ", program_line.vehicle_id.odometer
            ##print "program_line.vehicle_id.current_odometer_read: ", program_line.vehicle_id.current_odometer_read
            vehicle_obj = self.pool.get('fleet.vehicle')
            vehicle_obj.write(cr, uid, [program_line.vehicle_id.id], {'cycle_next_service' : program_line.mro_cycle_id.id, 
                                                                      'date_next_service' : program_line.next_date or time.strftime('%Y-%m-%d'), 
                                                                      'sequence_next_service' : program_line.sequence,
                                                                      'main_odometer_next_service' : program_line.trigger,
                                                                      'odometer_next_service' : program_line.trigger})
            ##print "Despues del desmadre..."
        
        return False


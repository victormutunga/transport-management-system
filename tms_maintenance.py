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



# Modificamos el objeto Vehiculo para agregar los campos requeridos para MRO
class fleet_vehicle(osv.osv):
    _name = 'fleet.vehicle'
    _inherit = ['fleet.vehicle']



    _columns = {

        'tires_number'               : fields.integer('Number of Tires'),
        'tires_extra'                : fields.integer('Number of Extra Tires'),
        'mro_program_id'             : fields.many2one('product.product', 'Maintenance Program', required=False, domain=[('tms_category','=','maint_service_program')]),
        'mro_cycle_ids'              : fields.one2many('fleet.vehicle.mro_program', 'vehicle_id', 'MRP Program'),

        'last_preventive_service'    : fields.many2one('tms.maintenance.order', 'Last Maintenance Service'),
        'main_odometer_last_service' : fields.related('last_preventive_service', 'odometer', type='float', string="Last Serv. Odometer", store=True, readonly=True),
        'odometer_last_service'      : fields.related('last_preventive_service', 'active_odometer', type='float', string="Last Serv. Active Odometer", store=True, readonly=True),
        'date_last_service'          : fields.related('last_preventive_service', 'date', type='datetime', string="Date Last Serv.", store=True, readonly=True),
        'sequence_last_service'      : fields.related('last_preventive_service', 'program_sequence', type='integer', string="Program Seq. Last Serv.", store=True, readonly=True),
        'cycle_last_service'         : fields.related('last_preventive_service', 'maint_cycle_id', type='many2one', relation='product.product', string='Cycle Last Serv.', store=True, readonly=True),


        'main_odometer_next_service' : fields.float('Odometer Next Serv.'),
        'odometer_next_service'      : fields.float('Active Odometer Next Serv.'),
        'date_next_service'          : fields.date('Date Next Serv.'),
        'sequence_next_service'      : fields.integer('Cycle Seq. Next Serv.'),
        'cycle_next_service'         : fields.many2one('product.product', 'Next Maintenance Service', domain=[('tms_category','=','maint_service_cycle')]),

        }


    def _check_next_service(self, cr, uid, ids, context=None):
        program_obj = self.pool.get('fleet.vehicle.mro_program')
        for record in self.browse(cr, uid, ids, context=context):
            print record.cycle_next_service.id
            print record.sequence_next_service
            print record.id
            if record.cycle_next_service.id and record.sequence_next_service:
                res = program_obj.search(cr, uid, [('vehicle_id', '=', record.id), ('mro_cycle_id', '=', record.cycle_next_service.id), ('sequence', '=', record.sequence_next_service)])
                print res
                return (len(res) > 0)
        return True

    _constraints = [
        (_check_next_service, 'Error ! Next service Cycle and Sequence was not found in Vehicle''s Program...', ['cycle_next_service'])
        ]



    def return_cycle_ids(self, cr, uid, ids, cycle_id, context=None):
        print "cycle_id: ", cycle_id
        ids = [0]
        if len(cycle_id) and cycle_id[0]:
            for cycle in self.pool.get('product.product').browse(cr, uid, cycle_id)[0].mro_cycle_ids: 
                ids.append(cycle.id)
                if cycle.mro_cycle_ids and len(cycle.mro_cycle_ids):
                    ids = ids + self.return_cycle_ids(cr, uid, ids, [cycle.id])
        return ids

    def button_create_mro_program(self, cr, uid, ids, context=None):
        vehicle =  self.browse(cr, uid, ids)[0]
        program_obj = self.pool.get('fleet.vehicle.mro_program')        
        prog_ids = program_obj.search(cr, uid, [('vehicle_id', '=', ids[0])])
        if len(prog_ids):
            program_obj.unlink(cr, uid, prog_ids)
        
        for cycle in vehicle.mro_program_id.mro_cycle_ids:
            seq = 1
            for x in range(cycle.mro_frequency, 3000000,cycle.mro_frequency): 
                program_obj.create(cr, uid, {'vehicle_id': ids[0], 'mro_cycle_id' : cycle.id, 'trigger' : x,  'sequence': seq})
                seq += 1
        
        seq = 1
        last_trigger = 0
        last_cycle_id = False
        for cycle in vehicle.mro_cycle_ids:
            if last_trigger == cycle.trigger and last_cycle_id and cycle.mro_cycle_id.id in self.return_cycle_ids(cr, uid, ids, [last_cycle_id]):
                    program_obj.unlink(cr, uid, cycle.id)
            else:
                last_trigger = cycle.trigger
                last_cycle_id = cycle.mro_cycle_id.id
                program_obj.write(cr, uid, cycle.id, { 'sequence': seq })
                seq += 1

        return True



class fleet_vehicle_mro_program(osv.Model):
    _name = 'fleet.vehicle.mro_program'
    _description = 'Fleet Vehicle MRO Program'

    _columns = {
        'vehicle_id'     : fields.many2one('fleet.vehicle', 'Vehicle', required=True),
        'mro_cycle_id'   : fields.many2one('product.product', 'MRO Cycle', required=True),
        'trigger'        : fields.integer('Triggered at', required=True),
        'sequence'       : fields.integer('Sequence', required=True),
        'mro_service_order_id'   : fields.many2one('tms.maintenance.order', 'MRO Service Order'),
        'mro_service_order_date' : fields.related('mro_service_order_id', 'date', type='datetime', string="Date", store=True, readonly=True),
        'next_date'     : fields.date('Date Next Service'),
        }

    _defaults = {
        'next_date'      : lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT),
        }

    _order = 'trigger, sequence'

    def button_set_next_cycle_service(self, cr, uid, ids, context=None):
        print "context: ", context
        if not ids:
            return False
        print "ids: ", ids
        for program_line in self.browse(cr, uid, ids):
            print "program_line.mro_cycle_id: ", program_line.mro_cycle_id
            print "program_line.sequence: ", program_line.sequence
            print "program_line.vehicle_id.odometer: ", program_line.vehicle_id.odometer
            print "program_line.vehicle_id.current_odometer_read: ", program_line.vehicle_id.current_odometer_read
            vehicle_obj = self.pool.get('fleet.vehicle')
            vehicle_obj.write(cr, uid, [program_line.vehicle_id.id], {'cycle_next_service' : program_line.mro_cycle_id.id, 
                                                                      'date_next_service' : program_line.next_date or time.strftime('%Y-%m-%d'), 
                                                                      'sequence_next_service' : program_line.sequence,
                                                                      'main_odometer_next_service' : program_line.trigger,
                                                                      'odometer_next_service' : program_line.trigger})
            print "Despues del desmadre..."
        
        return False


class fleet_vehicle_mro_program_reschedule(osv.osv_memory):
    _name ='fleet.vehicle.mro_program.re_schedule'
    _description = 'Fleet Vehicle MRO Program assignation'

    _columns = {
        'vehicle_id'     : fields.many2one('fleet.vehicle', 'Vehicle', required=True, readonly=True),
        'odometer'       : fields.float('Odometer', readonly=True),
        'mro_program_id' : fields.many2one('product.product', 'Maintenance Program', required=True, readonly=True),
        'next_date'      : fields.date('Date Next Service'),
        'mro_cycle_ids'  : fields.many2many('fleet.vehicle.mro_program', 'fleet_vehicle_mro_program_re_schedule_rel', 'vehicle_id', 'cycle_id', string='MRO Program', required=True),
        }



    def _get_vehicle_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('active_ids', False) 

    def _get_odometer(self, cr, uid, context=None):
        if context is None:
            context = {}
        vehicle_obj = self.pool.get('fleet.vehicle')
        vehicle_id = context.get('active_ids', [])
        if len(vehicle_id):
            for vehicle in vehicle_obj.browse(cr, uid, vehicle_id):
                return vehicle.odometer or False
        return False


    def _get_mro_program_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        print context

        vehicle_obj = self.pool.get('fleet.vehicle')
        vehicle_id = context.get('active_ids', [])
        if len(vehicle_id):
            for vehicle in vehicle_obj.browse(cr, uid, vehicle_id):
                return vehicle.mro_program_id.id or False
        return False


    def _get_mro_cycle_ids(self, cr, uid, context=None):
        if context is None:
            context = {}
        print context

        vehicle_obj = self.pool.get('fleet.vehicle')
        vehicle_id = context.get('active_ids', [])
        if len(vehicle_id):
            return self.pool.get('fleet.vehicle.mro_program').search(cr, uid ,[('vehicle_id', '=', vehicle_id[0]), ('mro_service_order_id', '=', False)])
        else:
            return False


    _defaults = {
        'vehicle_id'     : _get_vehicle_id,
        'odometer'       : _get_odometer,
        'mro_program_id' : _get_mro_program_id,
        'mro_cycle_ids'  : _get_mro_cycle_ids,
        'next_date'      : lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT),
        }


            


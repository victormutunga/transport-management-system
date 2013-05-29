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
        'cycle_next_service'         : fields.many2one('product.product', 'Next Maintenance Service', domain=[('tms_category','=','tms_maint_service')]),

        }


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
        
        print "============================"
        print "Eliminando los repetidos y que estan contenidos en el repetido..."
        
        last_trigger = 0
        last_cycle_id = False
        print "Antes de entrar al ciclo..."
        for cycle in vehicle.mro_cycle_ids:
            print "============================"
            print "En el ciclo ..."
            print "last_cycle_id: ", last_cycle_id
            print "cycle.mro_cycle_id.id: ", cycle.mro_cycle_id.id
            print "last_trigger: ", last_trigger
            print "cycle.name: ", cycle.mro_cycle_id.name
            print "cycle.trigger: ", cycle.trigger
            print "cycle.trigger == last_trigger: ", last_trigger == cycle.trigger

            print "cycle.id: ", cycle.id
            print "return_cycle_ids: ", self.return_cycle_ids(cr, uid, ids, [last_cycle_id])
            print "cycle.id in : ", cycle.id in self.return_cycle_ids(cr, uid, ids, [last_cycle_id])
            if last_trigger == cycle.trigger and last_cycle_id and cycle.mro_cycle_id.id in self.return_cycle_ids(cr, uid, ids, [last_cycle_id]):
                    program_obj.unlink(cr, uid, cycle.id)
            else:
                last_trigger = cycle.trigger
                last_cycle_id = cycle.mro_cycle_id.id

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
        }

    _order = 'trigger, sequence'




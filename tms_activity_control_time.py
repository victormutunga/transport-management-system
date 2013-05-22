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

class tms_activity_control_time(osv.Model):
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = 'tms.activity.control.time'
    _description = 'Activity Control Time'
    _rec_name='state'

########################### Columnas : Atributos #######################################################################
    _columns = {
        'state': openerp.osv.fields.selection([('draft','Draft'), ('process','Process'), ('pause','Pause'), ('end','End'), ('cancel','Cancel')],'State Activity'),
        #eventossssss  ('process','Process'), ('pause','Pause'), ('end','End')
        ########One2Many###########
        'tms_time_ids': fields.one2many('tms.time','control_time_id', readonly="True"),

        ########char###########
        'uid': fields.char('uid', readonly="True"),

        ######## Date ###########
        'date_begin': fields.datetime('Date Begin', readonly="True"),
        'date_end': fields.datetime('Date End', readonly="True"),

        ######## Many2One ###########
        'order_id': fields.many2one('tms.maintenance.order','Order', readonly="True"),
        'activity_id': fields.many2one('tms.maintenance.order.activity','Activity ID', readonly="True"),
        'hr_employee_id': fields.many2one('hr.employee','Mechanic', readonly="True"),
        'hr_employee_user_id': fields.many2one('res.users','User',readonly="True"),
        
        ## Float
        'hours_mechanic':      fields.float('Hours Work', readonly="True"),

        ######## Related ###########
        'name_order': fields.related('activity_id','maintenance_order_id', 'name', type='char', string='Order', readonly=True, store=True),
        'name_activity': fields.related('activity_id','product_id', 'name_template', type='char', string='Activity', readonly=True, store=True),
    }
    
########################### Metodos ####################################################################################

    def get_current_instance(self, cr, uid, ids):
        lines = self.browse(cr,uid,ids)
        obj = None
        for i in lines:
            obj = i
        return obj

    def get_time_lines(self,cr,uid,ids):
        this = self.get_current_instance(cr, uid, ids)       
        return this['tms_time_ids']

    def calculate_diference_time(self, cr, uid, ids, date_begin, date_end):
        this = self.get_current_instance(cr, uid, ids)
        duration = datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S') - datetime.strptime(date_begin, '%Y-%m-%d %H:%M:%S')
        x1 = (duration.seconds / 3600.0) + (duration.days / 24 ) 
        return x1

    def calculate_time_activity(self, cr, uid, ids):
        sum_time = 0.0
        
        temp_begin = -1

        for time in self.get_time_lines(cr,uid,ids):

            if time['event'] in 'process':
                temp_begin = time['date_event']

            if time['event'] in ('pause','end'):
                sum_time = sum_time + self.calculate_diference_time(cr, uid, ids, temp_begin, time['date_event'])

        return sum_time

    def create_time_rec(self,cr,uid,ids, date_event, event):
        
        this = self.get_current_instance(cr, uid, ids)

        vals_time = {
                ## One2Many Request, Many2One  de tms_time a tms_activity_control_time
                'control_time_id': ''+str( this['id'] ),
                'event':''+str(event),
                'date_event':date_event,
               } 

        time_id  = self.pool.get('tms.time').create(cr, uid, vals_time, None)
        time_obj = self.pool.get('tms.time').browse(cr, uid, time_id)

        ## One2Many a tms_time
        this['tms_time_ids'].append(str(time_obj['id']))
        return time_obj

    ########## Metodos para el 'state' ##########

    def action_start(self, cr, uid, ids, context=None):
        date_start = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.write(cr, uid, ids, {'date_begin':date_start})
        ## Fijar Suma Fecha Inicio Actividad en (order.activity) campo (date_start_real) 
        this = self.get_current_instance(cr, uid, ids)
        if this['activity_id']:
            this['activity_id'].write({'date_start_real':date_start})
 
        return self.action_process(cr, uid, ids, context)

    def action_process(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,{'state':'process'}) 
        self.create_time_rec(cr,uid,ids, time.strftime(DEFAULT_SERVER_DATETIME_FORMAT), 'process')
        return True

    def action_pause(self,cr,uid,ids,context=None): 
        self.write(cr, uid, ids, {'state':'pause'})
        self.create_time_rec(cr,uid,ids, time.strftime(DEFAULT_SERVER_DATETIME_FORMAT), 'pause')
        return True  

    def action_end(self,cr,uid,ids,context=None): 
        date_end = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        self.write(cr, uid, ids, {'state':'end'})
        self.write(cr, uid, ids, {'date_end':date_end}) 
        self.create_time_rec(cr,uid,ids, date_end, 'end')

        ## Fijar Suma Tiempos             en (order.activity) campo (hours_real)
        ## Fijar Suma Fecha Fin Actividad en (order.activity) campo (date_end_real) 
        this = self.get_current_instance(cr, uid, ids)
        if this['activity_id']:
            time_total_mechanic = self.calculate_time_activity(cr, uid, ids)
            this.write( {'hours_mechanic':time_total_mechanic})

            acumulate_of_activity = time_total_mechanic + this['activity_id']['hours_real']
            this['activity_id'].write( {'hours_real':acumulate_of_activity, 
                                        'date_end_real':date_end,
                                        'date_most_recent_end_mechanic_activity':date_end})
            this['activity_id']['maintenance_order_id'].calculate_cost_service()
        ##### Cerrar La Actividad Padre si es Posible   
        this['activity_id'].done_close_activity_if_is_posible()
        #####    
        return True 

    def action_cancel(self,cr,uid,ids,context=None): 
        self.write(cr, uid, ids, {'state':'cancel'})
        return True   

########################### Valores por Defecto ########################################################################
    _defaults = {
        'state'                 : lambda *a: 'draft',
    }

########################### Criterio de ordenamiento ###################################################################
    #_order = 'name'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

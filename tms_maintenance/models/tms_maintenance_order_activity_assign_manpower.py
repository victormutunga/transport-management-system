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
import pytz

# Wizard que permite asignar Mecánicos a una o varias Tareas a la vez
class tms_maintenance_order_activity_assign_manpower(osv.osv_memory):

    """ To assign internal manpower to several Tasks"""

    _name = 'tms.maintenance.order.activity.assing_manpower'
    _description = 'Assign internal Manpower to several Tasks'

    _columns = {
            
            'mechanic_ids': fields.many2many('hr.employee','tms_maintenance_order_assign_manpower_rel', 'activity_id','maintenance_id','Mechanics', 
                                            domain=[('tms_category', '=', 'mechanic')], required=True),
        }

    def assign_manpower(self, cr, uid, ids, context=None):

        """
             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param context: A standard dictionary

        """
        task_obj = self.pool.get('tms.maintenance.order.activity')
        task_ids =  context.get('active_ids',[])
        task_ids = task_obj.search(cr, uid, [('id','in',tuple(task_ids),),('state','=', 'pending')])
        if not task_ids:
            raise osv.except_osv(
                        _('Warning !'),
                        _('Please select at least one Task in Pending state to assign manpower'))
        rec = self.browse(cr,uid, ids)[0]
 
        mechanic_ids = [x.id for x in rec.mechanic_ids]
        if not mechanic_ids:
            raise osv.except_osv(
                            _('Warning !'),
                            _('Please select at least one Mechanic or Technical Staff to assign manpower to selected Tasks'))

        for record in task_obj.browse(cr, uid, task_ids):
            mechanics = [x.id for x in record.mechanic_ids]
            for mechanic_id in mechanic_ids:
                if mechanic_id not in mechanics:
                    mechanics.append(mechanic_id)
            if mechanics != [x.id for x in record.mechanic_ids]:
                task_obj.write(cr, uid, [record.id], {'mechanic_ids': [(6, 0, [x for x in mechanics])]})
        return {'type': 'ir.actions.act_window_close'}



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

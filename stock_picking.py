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
import netsvc
import pooler
from tools.translate import _
import decimal_precision as dp
from osv.orm import browse_record, browse_null
import time
from datetime import datetime, date

## Agregamos manejar una secuencia por cada tienda para controlar viajes 
class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"
    
    _columns = {
            'tms_order_id' : fields.many2one('tms.maintenance.order', 'Maintenance Order'),
            'unit_id'      : fields.related('tms_order_id','unit_id',type='many2one',relation='fleet.vehicle',string='Vehicle',store=True,readonly=True),
            'from_tms_order' : fields.boolean('From MRO Order'),
        }

    def action_cancel(self, cr, uid, ids, context=None):
        print '==============================================  stock_picking----action_cancel'
        print '==============================================  stock_picking----action_cancel'
        print '==============================================  stock_picking----action_cancel'
        band = super(stock_picking, self).action_cancel(cr, uid, ids, context)
        return band

    def action_confirm(self, cr, uid, ids, context=None):
        print '==============================================  stock_picking----action_confirm'
        print '==============================================  stock_picking----action_confirm'
        print '==============================================  stock_picking----action_confirm'
        band = super(stock_picking, self).action_confirm(cr, uid, ids, context)
        return band   

    #########################
    ############################
    ###############################
    ##################################
    #####################################
    
    def draft_force_assign(self, cr, uid, ids, *args):
        print '==============================================  stock_picking----draft_force_assign'
        print '==============================================  stock_picking----draft_force_assign'
        print '==============================================  stock_picking----draft_force_assign'
        band = super(stock_picking, self).draft_force_assign(cr, uid, ids, *args)
        return band    

    def draft_validate(self, cr, uid, ids, context=None):
        print '==============================================  stock_picking----draft_validate'
        print '==============================================  stock_picking----draft_validate'
        print '==============================================  stock_picking----draft_validate'
        band = super(stock_picking, self).draft_validate(cr, uid, ids, context)
        return band  

    def force_assign(self, cr, uid, ids, *args):
        print '==============================================  stock_picking----force_assign'
        print '==============================================  stock_picking----force_assign'
        print '==============================================  stock_picking----force_assign'
        diccionario_action_process = super(stock_picking, self).force_assign(cr, uid, ids, *args)
        return diccionario_action_process  

    def action_process(self, cr, uid, ids, context=None):
        print '==============================================  stock_picking----action_process'
        print '==============================================  stock_picking----action_process'
        print '==============================================  stock_picking----action_process'
        diccionario = super(stock_picking, self).action_process(cr, uid, ids, context)
        return diccionario  

    def action_move(self, cr, uid, ids, context=None):
        print '==============================================  stock_picking----action_move'
        print '==============================================  stock_picking----action_move'
        print '==============================================  stock_picking----action_move'
        band = super(stock_picking, self).action_move(cr, uid, ids, context)
        return band  

    def on_change_tms_order(self, cr, uid, ids, tms_order_id, context=None):
        return {'value': {'unit_id': self.pool.get('tms.maintenance.order').browse(cr, uid, [tms_order_id])[0].unit_id.id}}
    
    
    
stock_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

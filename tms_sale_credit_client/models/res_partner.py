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

### HERENCIA A CLIENTES PARA IGNORAR VENCIMIENTO ###
class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit ='res.partner'
    _columns = {
    'overdue_invoice': fields.boolean('Ignorar Facturas Vencidas', help='Si este campo esta Activo, las facturas Vencidas no afectaran si el Cliente aun tiene Credito'),

        }

    _defaults = {
        }
res_partner()


######### HERENCIA DE FACTURACION DESDE ALBARANES ##############
class stock_partial_picking(osv.osv):
    _name = 'stock.partial.picking'
    _inherit ='stock.partial.picking'
    _columns = {
        }

    def do_partial(self, cr, uid, ids, context=None):
        res = super(stock_partial_picking, self).do_partial(cr, uid, ids, context)
        
        return res

stock_partial_picking()
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
from tools.translate import _
from openerp import SUPERUSER_ID


class sale_order_extend_credit(osv.osv_memory):
    _name = 'sale.order.extend.credit'
    _description = 'Asistente para Extender el Credito'
    _columns = {
    'partner_id': fields.many2one('res.partner', 'Cliente', readonly=True),
    'credit': fields.float('Total a Cobrar', digits=(12,2), readonly=True),
    'credit_limit': fields.float('Credito Concedito', digits=(12,2), readonly=True),
    'credit_extend': fields.float('Credito Nuevo', digits=(12,2), required=True, help='Indica el Nuevo Monto Autorizado de Credito, por defecto como sugerencia el Sistema Suma el Credito que Adeuda el Cliente + el monto del pedido de Venta' ),
    'password' : fields.char('Contraseña del Usuario', size=128, required=True),
    }

    def _get_partner(self, cr, uid, context=None):
        active_id = context.get('active_id', False)
        sale_obj = self.pool.get('account.invoice')
        sale_br = sale_obj.browse(cr, uid, [active_id], context=None)[0]
        return sale_br.partner_id.id

    def _get_credit(self, cr, uid, context=None):
        active_id = context.get('active_id', False)
        sale_obj = self.pool.get('account.invoice')
        sale_br = sale_obj.browse(cr, uid, [active_id], context=None)[0]
        return sale_br.partner_id.credit

    def _get_limit(self, cr, uid, context=None):
        active_id = context.get('active_id', False)
        sale_obj = self.pool.get('account.invoice')
        sale_br = sale_obj.browse(cr, uid, [active_id], context=None)[0]
        return sale_br.partner_id.credit_limit

    def _get_credit_new(self, cr, uid, context=None):
        active_id = context.get('active_id', False)
        sale_obj = self.pool.get('account.invoice')
        sale_br = sale_obj.browse(cr, uid, [active_id], context=None)[0]
        credit_extend = sale_br.partner_id.credit + sale_br.amount_total
        return credit_extend

    _defaults = {

    'partner_id': _get_partner,
    'credit': _get_credit,
    'credit_limit': _get_limit,
    'credit_extend': _get_credit_new,

        }

    def auth(self, cr, uid, ids, context=None):
        active_ids = context.get('active_ids', False)
        password = self.browse(cr, SUPERUSER_ID, ids, context=None)[0].password
        group_obj = self.pool.get('res.groups')
        group_id = group_obj.search(cr, SUPERUSER_ID, [('name','=','Ventas / Permisos Especiales')])
        users_obj = self.pool.get('res.users')
        user_list = []
        sale_order_obj = self.pool.get('account.invoice')
        for group in group_obj.browse(cr, SUPERUSER_ID, group_id, context=None):
            for user in group.users:
                user_list.append(user.id)
        if user_list:
            user_ids = users_obj.search(cr, SUPERUSER_ID, [('password','=',password),('id','in',tuple(user_list))])
            if user_ids:
                if active_ids:
                    partner_obj = self.pool.get('res.partner')
                    for rec in self.browse(cr, uid, ids, context=None):
                        sale_order_obj.write(cr, uid, active_ids, {'exced_credit': False})
                        partner_obj.write(cr, uid, [rec.partner_id.id], {'credit_limit': rec.credit_extend})
                return {'type' : 'ir.actions.act_window_close' }
            else:
                raise osv.except_osv(
                                    _('Error ! \n La Contraseña es Incorrecta o el Usuario no tiene Permisos.'),
                                    _('Consulte a su Administrador y Verifique que el usuario se encuentra en el Grupo [Ventas / Permisos Especiales]'))

        else:
            raise osv.except_osv(
                    _('Error ! \n La Contraseña es Incorrecta o el Usuario no tiene Permisos.'),
                    _('Consulte a su Administrador y Verifique que el usuario se encuentra en el Grupo [Ventas / Permisos Especiales]'))
        return {'type' : 'ir.actions.act_window_close' }

sale_order_extend_credit()


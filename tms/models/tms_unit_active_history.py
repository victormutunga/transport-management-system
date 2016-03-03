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


from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time


#Unit Active / Inactive history
class tms_unit_active_history(osv.osv):
    _name = "tms.unit.active_history"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Units Active / Inactive history"

    _columns = {
        'state'             : fields.selection([('draft','Draft'), ('confirmed','Confirmed'), ('cancel','Cancelled')], 'State', readonly=True),
        'unit_id'           : fields.many2one('fleet.vehicle', 'Unit Name', required=True, ondelete='cascade', domain=[('active', 'in', ('true', 'false'))]),
        'unit_type_id'      : fields.related('unit_id', 'unit_type_id', type='many2one', relation='tms.unit.category', store=True, string='Unit Type'),
        'prev_state'        : fields.selection([('active','Active'), ('inactive','Inactive')], 'Previous State', readonly=True),
        'new_state'         : fields.selection([('active','Active'), ('inactive','Inactive')], 'New State', readonly=True),
        'date'              : fields.datetime('Date', states={'cancel':[('readonly',True)], 'confirmed':[('readonly',True)]}, required=True),
        'state_cause_id'    : fields.many2one('tms.unit.category', 'Active/Inactive Cause', domain="[('type','=','active_cause')]", states={'cancel':[('readonly',True)], 'confirmed':[('readonly',True)]}, required=True),
        'name'              : fields.char('Description', size=64, states={'cancel':[('readonly',True)], 'confirmed':[('readonly',True)]}, required=True),
        'notes'             : fields.text('Notes', states={'cancel':[('readonly',True)], 'confirmed':[('readonly',True)]}, required=False),
        'create_uid'        : fields.many2one('res.users', 'Created by', readonly=True),
        'create_date'       : fields.datetime('Creation Date', readonly=True, select=True),
        'confirmed_by'      : fields.many2one('res.users', 'Confirmed by', readonly=True),
        'date_confirmed'    : fields.datetime('Date Confirmed', readonly=True),
        'cancelled_by'      : fields.many2one('res.users', 'Cancelled by', readonly=True),
        'date_cancelled'    : fields.datetime('Date Cancelled', readonly=True),
        }

    _defaults = {
        'state'     : lambda *a: 'draft',
        'date'      : lambda *a: time.strftime( DEFAULT_SERVER_DATETIME_FORMAT),
        }

    def on_change_state_cause_id(self, cr, uid, ids, state_cause_id):
        return {'value': {'name': self.pool.get('tms.unit.category').browse(cr, uid, [state_cause_id])[0].name }}

    def on_change_unit_id(self, cr, uid, ids, unit_id):
        val = {}
        if not unit_id:
            return  val
        for rec in self.pool.get('fleet.vehicle').browse(cr, uid, [unit_id]):
            val = {'value' : {'prev_state' : 'active' if rec.active else 'inactive','new_state' : 'inactive' if rec.active else 'active' } }
        return val

    def create(self, cr, uid, vals, context=None):
        values = vals
        if 'unit_id' in vals:
            res = self.search(cr, uid, [('unit_id', '=', vals['unit_id']),('state','=','draft')], context=None)
            if res and res[0]:
                raise osv.except_osv(
                        _('Warning!'),
                        _('You can not create a new record for this unit because theres is already a record for this unit in Draft State.'))
            unit_obj = self.pool.get('fleet.vehicle')
            for rec in unit_obj.browse(cr, uid, [vals['unit_id']]):
                vals.update({
                                'prev_state' : 'active' if rec.active else 'inactive',
                                'new_state'  : 'inactive' if rec.active else 'active' }
                            )
        ##print vals
        return super(tms_unit_active_history, self).create(cr, uid, values, context=context)

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            if rec.state == 'confirmed':
                raise osv.except_osv(
                        _('Warning!'),
                        _('You can not delete a record if is already Confirmed!!! Click Cancel button to continue.'))
        super(tms_unit_active_history, self).unlink(cr, uid, ids, context=context)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            if rec.state == 'confirmed':
                raise osv.except_osv(
                        _('Warning!'),
                        _('You can not cancel a record if is already Confirmed!!!'))
        self.write(cr, uid, ids, {'state':'cancel', 'cancelled_by' : uid, 'date_cancelled':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_confirm(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            ##print rec.new_state == 'active'
            self.pool.get('fleet.vehicle').write(cr, uid, [rec.unit_id.id], {'active' : (rec.new_state == 'active')} )
        self.write(cr, uid, ids, {'state':'confirmed', 'confirmed_by' : uid, 'date_confirmed':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True
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
import openerp.addons.decimal_precision as dp
import time


# Unit Red Tape
class tms_unit_red_tape(osv.osv):
    _name = "tms.unit.red_tape"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Units Red Tape history"

    _columns = {
        'state'             : fields.selection([('draft','Draft'), ('pending','Pending'), ('progress','Progress'), ('done','Done'), ('cancel','Cancelled')], 'State', readonly=True),
        'unit_id'           : fields.many2one('fleet.vehicle', 'Unit Name', required=True, ondelete='cascade', domain=[('active', 'in', ('true', 'false'))],
                                                            readonly=True, states={'draft':[('readonly',False)]} ),
        'unit_type_id'      : fields.related('unit_id', 'unit_type_id', type='many2one', relation='tms.unit.category', store=True, string='Unit Type', readonly=True),
        'date'              : fields.datetime('Date', required=True, readonly=True, states={'draft':[('readonly',False)], 'pending':[('readonly',False)]} ),
        'date_start'        : fields.datetime('Date Start', readonly=True),
        'date_end'          : fields.datetime('Date End', readonly=True),
        'red_tape_id'       : fields.many2one('tms.unit.category', 'Red Tape', domain="[('type','=','red_tape')]",  required=True,
                                readonly=True, states={'draft':[('readonly',False)]} ),
        'partner_id'        : fields.many2one('res.partner', 'Partner', states={'cancel':[('readonly',True)], 'done':[('readonly',True)]}, required=False),
        'name'              : fields.char('Description', size=64, required=True, readonly=True, states={'draft':[('readonly',False)], 'pending':[('readonly',False)]} ),
        'notes'             : fields.text('Notes', states={'cancel':[('readonly',True)], 'done':[('readonly',True)]}, required=False),
        'amount'            : fields.float('Amount', required=True, digits_compute= dp.get_precision('Sale Price'), readonly=False, states={'cancel':[('readonly',True)], 'done':[('readonly',True)]} ),
        'amount_paid'       : fields.float('Amount Paid', required=True, digits_compute= dp.get_precision('Sale Price'), readonly=False, states={'cancel':[('readonly',True)], 'done':[('readonly',True)]} ),
        'create_uid'        : fields.many2one('res.users', 'Created by', readonly=True),
        'create_date'       : fields.datetime('Creation Date', readonly=True, select=True),
        'pending_by'        : fields.many2one('res.users', 'Pending by', readonly=True),
        'date_pending'      : fields.datetime('Date Pending', readonly=True),
        'progress_by'       : fields.many2one('res.users', 'Progress by', readonly=True),
        'date_progress'     : fields.datetime('Date Progress', readonly=True),
        'done_by'           : fields.many2one('res.users', 'Done by', readonly=True),
        'date_done'         : fields.datetime('Date Done', readonly=True),
        'cancelled_by'      : fields.many2one('res.users', 'Cancelled by', readonly=True),
        'date_cancelled'    : fields.datetime('Date Cancelled', readonly=True),
        'drafted_by'        : fields.many2one('res.users', 'Drafted by', readonly=True),
        'date_drafted'      : fields.datetime('Date Drafted', readonly=True),
        }

    _defaults = {
        'state'       : lambda *a: 'draft',
        'date'        : lambda *a: time.strftime( DEFAULT_SERVER_DATETIME_FORMAT),
        'amount'      : 0.0,
        'amount_paid' : 0.0,
        }

    def on_change_red_tape_id(self, cr, uid, ids, red_tape_id):
        return {'value': {'name': self.pool.get('tms.unit.category').browse(cr, uid, [red_tape_id])[0].name }}

    def create(self, cr, uid, vals, context=None):
        if 'unit_id' in vals:
            res = self.search(cr, uid, [('unit_id', '=', vals['unit_id']),('state','=','draft')], context=None)
            if res and res[0]:
                raise osv.except_osv(
                        _('Warning!'),
                        _('You can not create a new record for this unit because theres is already a record for this unit in Draft State.'))
        return super(tms_unit_red_tape, self).create(cr, uid, vals, context=context)

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
                        _('You can not cancel a record if already Confirmed!!!'))
        self.write(cr, uid, ids, {'state':'cancel', 'cancelled_by' : uid, 'date_cancelled':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_pending(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'pending', 'pending_by' : uid, 'date_pending':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_cancel_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft', 'drafted_by' : uid, 'date_drafted':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_progress(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'progress', 'progress_by' : uid, 
                                    'date_progress':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                    'date_start':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                                    })
        return True

    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'done', 'done_by' : uid, 
                                  'date_done':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                  'date_end':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                                  })
        return True

# Causes for active / inactive transportation units   
# Pendiente

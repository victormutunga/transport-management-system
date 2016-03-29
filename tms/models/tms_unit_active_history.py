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

import time

from openerp import fields, models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _

# Unit Active / Inactive history


class TmsUnitActiveHistory(models.Model):
    _name = "tms.unit.active_history"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Units Active / Inactive history"

    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'),
         ('cancel', 'Cancelled')], 'State', readonly=True,
        default=(lambda *a: 'draft'))
    unit_id = fields.Many2one(
        'fleet.vehicle', 'Unit Name', required=True, ondelete='cascade',
        domain=[('active', 'in', ('true', 'false'))])
    unit_type_id = fields.Many2one(
        'tms.unit.category',
        string='Unit Type',
        related='unit_id.unit_type_id',
        store=True)
    prev_state = fields.Selection(
        [('active', 'Active'), ('inactive', 'Inactive')],
        'Previous State', readonly=True)
    new_state = fields.Selection(
        [('active', 'Active'), ('inactive', 'Inactive')],
        'New State', readonly=True)
    date = fields.Datetime(
        'Date', states={'cancel': [('readonly', True)],
                        'confirmed': [('readonly', True)]}, required=True,
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    state_cause_id = fields.Many2one(
        'tms.unit.category', 'Active/Inactive Cause',
        domain="[('type','=','active_cause')]",
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)]}, required=True)
    name = fields.Char(
        'Description', size=64, states={'cancel': [('readonly', True)],
                                        'confirmed': [('readonly', True)]},
        required=True)
    notes = fields.Text(
        'Notes', states={'cancel': [('readonly', True)],
                         'confirmed': [('readonly', True)]}, required=False)
    create_uid = fields.Many2one('res.users', 'Created by', readonly=True)
    create_date = fields.Datetime('Creation Date', readonly=True, select=True)
    confirmed_by = fields.Many2one('res.users', 'Confirmed by', readonly=True)
    date_confirmed = fields.Datetime('Date Confirmed', readonly=True)
    cancelled_by = fields.Many2one('res.users', 'Cancelled by', readonly=True)
    date_cancelled = fields.Datetime('Date Cancelled', readonly=True)

    def on_change_state_cause_id(self, state_cause_id):
        # return {'value': {
        #     'name': self.pool.get(
        #         'tms.unit.category').browse([state_cause_id])[0].name}}
        return 'comida'

    def on_change_unit_id(self, unit_id):
        # val = {}
        # if not unit_id:
        #     return val
        # for rec in self.pool.get('fleet.vehicle').browse([unit_id]):
        #     val = {'value': {
        #         'prev_state': 'active' if rec.active else 'inactive',
        #         'new_state': 'inactive' if rec.active else 'active'}}
        # return val
        return 'comida'

    def create(self, vals):
        # values = vals
        # if 'unit_id' in vals:
        #     res = self.search(
        #         [('unit_id', '=', vals['unit_id']),
        #          ('state', '=', 'draft')], context=None)
        #     if res and res[0]:
        #         raise Warning(
        #             _('Warning!'),
        #           _('You can not create a new record for this unit because \
        #           theres is already a record for this unit in Draft State.'))
        #     unit_obj = self.pool.get('fleet.vehicle')
        #     for rec in unit_obj.browse([vals['unit_id']]):
        #         vals.update({
        #             'prev_state': 'active' if rec.active else 'inactive',
        #             'new_state': 'inactive' if rec.active else 'active'}
        #         )
        # # #print vals
        # return super(TmsUnitActiveHistory, self).create(values)
        return 'comida'

    def unlink(self):
        # for rec in self.browse(self):
        #     if rec.state == 'confirmed':
        #         raise Warning(
        #             _('Warning!'),
        #          _('You can not delete a record if is already Confirmed!!! \
        #                 Click Cancel button to continue.'))
        # super(TmsUnitActiveHistory, self).unlink(self)
        # return True
        return 'comida'

    def action_cancel(self):
        # for rec in self.browse(self):
        #     if rec.state == 'confirmed':
        #         raise Warning(
        #             _('Warning!'),
        #          _('You can not cancel a record if is already Confirmed!!'))
        # self.write({
        #     'state': 'cancel',
        #     'cancelled_by': self,
        #     'date_cancelled': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        # return True
        return 'comida'

    def action_confirm(self):
        # for rec in self.browse(self):
        #     # #print rec.new_state == 'active'
        #     self.pool.get('fleet.vehicle').write(
        #         [rec.unit_id.id], {
        #             'active': (rec.new_state == 'active')})
        # self.write({
        #     'state': 'confirmed',
        #     'confirmed_by': self,
        #     'date_confirmed':
        #     time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        # return True
        return 'comida'

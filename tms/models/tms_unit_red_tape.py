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
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _


# Unit Red Tape
class TmsUnitRedTape(models.Model):
    _name = "tms.unit.red_tape"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Units Red Tape history"

    state = fields.Selection(
        [('draft', 'Draft'), ('pending', 'Pending'), ('progress', 'Progress'),
         ('done', 'Done'), ('cancel', 'Cancelled')], 'State', readonly=True,
        default=(lambda *a: 'draft'))
    unit_id = fields.Many2one(
        'fleet.vehicle', 'Unit Name', required=True, ondelete='cascade',
        domain=[('active', 'in', ('true', 'false'))], readonly=True,
        states={'draft': [('readonly', False)]})
    unit_type_id = fields.Many2one(
        'tms.unit.category',
        string='Unit Type',
        related='unit_id.unit_type_id',
        store=True)
    date = fields.Datetime(
        'Date', required=True, readonly=True,
        states={'draft': [('readonly', False)],
                'pending': [('readonly', False)]},
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_start = fields.Datetime('Date Start', readonly=True)
    date_end = fields.Datetime('Date End', readonly=True)
    red_tape_id = fields.Many2one(
        'tms.unit.category', 'Red Tape', domain="[('type','=','red_tape')]",
        required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one(
        'res.partner', 'Partner', states={'cancel': [('readonly', True)],
                                          'done': [('readonly', True)]},
        required=False)
    name = fields.Char(
        'Description', size=64, required=True, readonly=True,
        states={'draft': [('readonly', False)],
                'pending': [('readonly', False)]})
    notes = fields.Text(
        'Notes', states={'cancel': [('readonly', True)],
                         'done': [('readonly', True)]},
        required=False)
    amount = fields.Float(
        'Amount', required=True, digits_compute=dp.get_precision('Sale Price'),
        readonly=False,
        states={'cancel': [('readonly', True)],
                'done': [('readonly', True)]}, default=0.0)
    amount_paid = fields.Float(
        'Amount Paid', required=True,
        digits_compute=dp.get_precision('Sale Price'), readonly=False,
        states={'cancel': [('readonly', True)],
                'done': [('readonly', True)]}, default=0.0)
    create_uid = fields.Many2one('res.users', 'Created by', readonly=True)
    create_date = fields.Datetime('Creation Date', readonly=True, select=True)
    pending_by = fields.Many2one('res.users', 'Pending by', readonly=True)
    date_pending = fields.Datetime('Date Pending', readonly=True)
    progress_by = fields.Many2one('res.users', 'Progress by', readonly=True)
    date_progress = fields.Datetime('Date Progress', readonly=True)
    done_by = fields.Many2one('res.users', 'Done by', readonly=True)
    date_done = fields.Datetime('Date Done', readonly=True)
    cancelled_by = fields.Many2one('res.users', 'Cancelled by', readonly=True)
    date_cancelled = fields.Datetime('Date Cancelled', readonly=True)
    drafted_by = fields.Many2one('res.users', 'Drafted by', readonly=True)
    date_drafted = fields.Datetime('Date Drafted', readonly=True)

    def on_change_red_tape_id(self, red_tape_id):
        return {'value': {
            'name': self.pool.get('tms.unit.category').browse(
                [red_tape_id])[0].name}}

    def create(self):
        if 'unit_id' in self:
            res = self.search(
                [('unit_id', '=', self['unit_id']),
                 ('state', '=', 'draft')], context=None)
            if res and res[0]:
                raise Warning(
                    _('Warning!'),
                    _('You can not create a new record for this unit \
                    because theres is already a record for this unit \
                    in Draft State.'))
        return super(TmsUnitRedTape, self).create(self)

    def unlink(self):
        for rec in self.browse(self):
            if rec.state == 'confirmed':
                raise Warning(
                    _('Warning!'),
                    _('You can not delete a record if is already Confirmed!!! \
                        Click Cancel button to continue.'))

        super(TmsUnitRedTape, self).unlink(self)
        return True

    def action_cancel(self):
        for rec in self.browse(self):
            if rec.state == 'confirmed':
                raise Warning(
                    _('Warning!'),
                    _('You can not cancel a record if already \
                            Confirmed!!!'))
        self.write(
            {'state': 'cancel', 'cancelled_by': self,
             'date_cancelled': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_pending(self):
        self.write(
            {'state': 'pending', 'pending_by': self,
             'date_pending': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_cancel_draft(self):
        self.write(
            {'state': 'draft', 'drafted_by': self,
             'date_drafted': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_progress(self):
        self.write({
            'state': 'progress', 'progress_by': self,
            'date_progress': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'date_start': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        })
        return True

    def action_done(self):
        self.write({
            'state': 'done', 'done_by': self,
            'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'date_end': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        })
        return True

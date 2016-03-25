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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


# Travel - Money operation payments for Travel expenses

class TmsOperation(models.Model):
    _name = 'tms.operation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Travel Operations'

    name = fields.Char('Operation', size=128, required=True),
    state = fields.Selection(
        [('draft', 'Draft'), ('process', 'Process'),
         ('done', 'Done'), ('cancel', 'Cancelled')],
        'State', readonly=True, required=True,
        default=(lambda *a: 'draft'))
    date = fields.Date(
        'Date', states={'cancel': [('readonly', True)],
                        'process': [('readonly', True)],
                        'done': [('readonly', True)]}, required=True,
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT)))
    partner_id = fields.Many2one(
        'res.partner', 'Customer', required=True, readonly=False,
        states={'cancel': [('readonly', True)], 'done': [('readonly', True)]})
    date_start = fields.Datetime(
        'Starting Date', states={'cancel': [('readonly', True)],
                                 'done': [('readonly', True)]}, required=True,
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_end = fields.Datetime(
        'Ending Date', states={'cancel': [('readonly', True)],
                               'done': [('readonly', True)]}, required=True,
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    notes = fields.Text(
        'Notes', states={'cancel': [('readonly', True)],
                         'done': [('readonly', True)]})
    create_uid = fields.Many2one('res.users', 'Created by', readonly=True)
    create_date = fields.Datetime('Creation Date', readonly=True, select=True)
    cancelled_by = fields.Many2one('res.users', 'Cancelled by', readonly=True)
    date_cancelled = fields.Datetime('Date Cancelled', readonly=True)
    process_by = fields.Many2one('res.users', 'Approved by', readonly=True)
    date_process = fields.Datetime('Date Approved', readonly=True)
    done_by = fields.Many2one('res.users', 'Confirmed by', readonly=True)
    date_done = fields.Datetime('Date Confirmed', readonly=True)
    drafted_by = fields.Many2one('res.users', 'Drafted by', readonly=True)
    date_drafted = fields.Datetime('Date Drafted', readonly=True)
    fuelvoucher_ids = fields.One2many(
        'tms.fuelvoucher', 'operation_id', string='Fuel Vouchers',
        readonly=True)
    advance_ids = fields.One2many(
        'tms.advance', 'operation_id', string='Expense Advance', readonly=True)
    waybill_ids = fields.One2many(
        'tms.waybill', 'operation_id', string='Waybills', readonly=True)
    expense_line_ids = fields.One2many(
        'tms.expense.line', 'operation_id', string='Travel Expense Lines',
        readonly=True)

    _sql_constraints = [(
        'name_uniq', 'unique(name)', 'Operation must be unique !')]
    _order = "date desc, name desc"

    def action_cancel_draft(self):
        if not len(self):
            return False
        for operation in self.browse(self):
            self.write({
                'state': 'draft', 'drafted_by': self,
                'date_drafted':
                    time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_cancel(self):
        for operation in self.browse(self):
            self.write({
                'state': 'cancel', 'cancelled_by': self,
                'date_cancelled':
                    time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_process(self):
        for operation in self.browse(self):
            self.write({
                'state': 'process', 'process_by': self,
                'date_process':
                    time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_done(self):
        for operation in self.browse(self):
            self.write({
                'state': 'done', 'done_by': self,
                'date_process':
                    time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def copy(self, default=None):
        default = default or {}
        default.update({
            'name': default['name'] + ' copy',
            'cancelled_by': False,
            'date_cancelled': False,
            'process_by': False,
            'date_process': False,
            'done_by': False,
            'date_done': False,
            'drafted_by': False,
            'date_drafted': False,
            'notes': False,
        })
        return super(TmsOperation, self).copy(id)

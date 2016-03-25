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

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _


# Travel - Money advance payments for Travel expenses
class TmsAdvance(models.Model):
    _name = 'tms.advance'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Money advance payments for Travel expenses'

    def _paid(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            val = False
            if record.move_id.id:
                for ml in record.move_id.line_id:
                    if (ml.credit > 0 and
                            record.employee_id.address_home_id.id ==
                            ml.partner_id.id):
                        val = (ml.reconcile_id.id or
                               ml.reconcile_partial_id.id)
            res[record.id] = val
        return res

    def _amount(self, field_name):
        res = {}
        for record in self.browse(self):
            tax_factor = 0.00
            for line in record.product_id.supplier_taxes_id:
                tax_factor = ((tax_factor + line.amount) if
                              line.amount != 0.0 else tax_factor)

            subtotal = record.price_unit * record.product_uom_qty
            tax_amount = subtotal * tax_factor
            res[record.id] = {
                'subtotal': subtotal,
                'tax_amount': tax_amount,
                # 'total'     :   total,
            }
        return res

    @api.multi
    def _get_move_line_from_reconcile(self):
        move = {}
        for r in self.env('account.move.reconcile').browse():
            for line in r.line_partial_ids:
                move[line.move_id.id] = True
            for line in r.line_id:
                move[line.move_id.id] = True
        advance_ids = []
        if move:
            advance_ids = self.env('tms.advance').search(
                [('move_id', 'in', move.keys())])
        return advance_ids

    # operation_id = fields.Many2one(
    #     'tms.operation', 'Operation', ondelete='restrict', required=False,
    #     readonly=False,
    #     states={'cancel': [('readonly', True)],
    #             'confirmed': [('readonly', True)],
    #             'closed': [('readonly', True)]})
    name = fields.Char('Anticipo', size=64, required=False)
    state = fields.Selection(
        [('draft', 'Draft'), ('approved', 'Approved'),
         ('confirmed', 'Confirmed'), ('closed', 'Closed'),
         ('cancel', 'Cancelled')], 'State', readonly=True,
        default=(lambda *a: 'draft'))
    date = fields.Date(
        'Date',
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]}, required=True,
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT)))
    travel_id = fields.Many2one(
        'tms.travel', 'Travel', required=True,
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]})
    unit_id = fields.Many2one(
        related='travel_id.unit_id', relation='fleet.vehicle',
        string='Unit', store=True, readonly=True)
    employee1_id = fields.Many2one(
        related='travel_id.employee_id', relation='hr.employee',
        string='Driver', store=True, readonly=True)
    employee2_id = fields.Many2one(
        related='travel_id.employee2_id', relation='hr.employee',
        string='Driver Helper', store=True, readonly=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Driver',
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]}, required=True)
    # shop_id = fields.Many2one('sale.shop', string='Shop')
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('purchase_ok', '=', 1),
                ('tms_category', '=', 'real_expense')],
        required=True, states={'cancel': [('readonly', True)],
                               'confirmed': [('readonly', True)],
                               'closed': [('readonly', True)]},
        ondelete='restrict')
    product_uom_qty = fields.Float(
        'Quantity', digits=(16, 4), required=True,
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=1)
    product_uom = fields.Many2one(
        'product.uom', 'Unit of Measure ', required=True,
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]})
    price_unit = fields.Float(
        'Price Unit', required=True,
        digits_compute=dp.get_precision('Sale Price'))
    price_unit_control = fields.Float(
        'Price Unit', digits_compute=dp.get_precision('Sale Price'),
        readonly=True)
    subtotal = fields.Float(
        compute=_amount, method=True, string='Subtotal',
        digits_compute=dp.get_precision('Sale Price'), multi=True,
        store=True)
    tax_amount = fields.Float(
        compute=_amount, method=True, string='Tax Amount',
        digits_compute=dp.get_precision('Sale Price'),
        multi=True, store=True)
    total = fields.Float(
        'Total', required=True, digits_compute=dp.get_precision('Sale Price'),
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]})
    notes = fields.Text(
        'Notes', states={'cancel': [('readonly', True)],
                         'confirmed': [('readonly', True)],
                         'closed': [('readonly', True)]})
    create_uid = fields.Many2one('res.users', 'Created by', readonly=True)
    create_date = fields.Datetime('Creation Date', readonly=True, select=True)
    cancelled_by = fields.Many2one('res.users', 'Cancelled by', readonly=True)
    date_cancelled = fields.Datetime('Date Cancelled', readonly=True)
    approved_by = fields.Many2one('res.users', 'Approved by', readonly=True)
    date_approved = fields.Datetime('Date Approved', readonly=True)
    confirmed_by = fields.Many2one('res.users', 'Confirmed by', readonly=True)
    date_confirmed = fields.Datetime('Date Confirmed', readonly=True)
    closed_by = fields.Many2one('res.users', 'Closed by', readonly=True)
    date_closed = fields.Datetime('Date Closed', readonly=True)
    drafted_by = fields.Many2one('res.users', 'Drafted by', readonly=True)
    date_drafted = fields.Datetime('Date Drafted', readonly=True)
    move_id = fields.Many2one(
        'account.move', 'Journal Entry', readonly=True, select=1,
        ondelete='restrict',
        help="Link to the automatically generated Journal Items.\nThis move \
        is only for Travel Expense Records with balance < 0.0")
    paid = fields.Boolean(
        compute=_paid, method=True, string='Paid', multi=False,
        store={'account.move.reconcile': (
            _get_move_line_from_reconcile, None, 50)})
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=(lambda self, cr, uid, c: self.pool.get('res.users').browse(
            cr, uid, uid, c).company_id.currency_id.id))
    auto_expense = fields.Boolean(
        'Auto Expense',
        help="Check this if you want this product and amount to be \
        automatically created when Travel Expense Record is created.",
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]})
    driver_helper = fields.Boolean(
        'For Driver Helper',
        help="Check this if you want to give this advance to \
        Driver Helper.",
        states={'cancel': [('readonly', True)],
                'approved': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]})
    expense_id = fields.Many2one(
        'tms.expense', 'Expense Record', required=False, readonly=True)
    expense2_id = fields.Many2one(
        'tms.expense', 'Expense Record for Drivef Helper',
        required=False, readonly=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Advance number must be unique !'),
    ]
    _order = "name desc, date desc"

    def on_change_price_total(self, product_id, product_uom_qty, price_total):
        res = {}
        if not (product_uom_qty and product_id and price_total):
            return res
        tax_factor = 0.00
        prod_obj = self.pool.get('product.product')
        for line in prod_obj.browse(
                [product_id], context=None)[0].supplier_taxes_id:
            tax_factor = (
                (tax_factor + line.amount)
                if line.amount != 0.0 else tax_factor)
        price_unit = price_total / (1.0 + tax_factor) / product_uom_qty
        price_subtotal = price_unit * product_uom_qty
        tax_amount = price_subtotal * tax_factor
        res = {'value': {
            'price_unit': price_unit,
            'price_unit_control': price_unit,
            'price_subtotal': price_subtotal,
            'tax_amount': tax_amount,
        }}
        return res

    def on_change_product_id(self, product_id):
        # res = {}
        if not product_id:
            return {}
        prod_obj = self.pool.get('product.product')
        prod = prod_obj.browse([product_id], context=None)
        return {'value': {'product_uom': prod[0].uom_id.id}}

    def on_change_driver_helper(
            self, driver_helper, employee1_id, employee2_id):
        return ({'value': {'employee_id': employee2_id, }}
                if driver_helper
                else {'value': {'employee_id': employee1_id, }})

    def on_change_driver(self, employee_id, employee1_id, employee2_id):
        return {'value': {'driver_helper': (employee_id == employee2_id)}}

    def on_change_travel_id(self, travel_id):
        if not travel_id:
            return {'value':
                    {
                        'employee_id': False,
                        'employee1_id': False,
                        'employee2_id': False,
                        'unit_id': False,
                        'operation_id': False,
                        'shop_id': False,
                    }}
        travel = self.pool.get('tms.travel').browse(
            [travel_id], context=None)[0]
        return {'value': {'employee_id': travel.employee_id.id,
                          'employee1_id': travel.employee_id.id,
                          'employee2_id': travel.employee2_id.id,
                          'unit_id': travel.unit_id.id,
                          'operation_id': travel.operation_id.id,
                          'shop_id': travel.shop_id.id,
                          }
                }

    def create(self, vals, context=None):
        travel = self.pool.get('tms.travel').browse(vals['travel_id'])
        shop_id = travel.shop_id.id
        shop = self.pool.get('sale.shop').browse([shop_id])[0]
        seq_id = shop.tms_advance_seq.id
        if shop.tms_advance_seq:
            seq_number = self.pool.get('ir.sequence').get_id(seq_id)
            vals['name'] = seq_number
        else:
            raise Warning(
                _('Travel Sequence Error !'),
                _('You have not defined Advance Sequence \
                    for shop ' + shop.name))
        return super(TmsAdvance, self).create(vals, context=context)

    def action_cancel_draft(self, ids, uid, *args):
        if not len(ids):
            return False
        for advance in self.browse(self):
            if advance.travel_id.state in ('cancel', 'closed'):
                raise Warning(
                    _('Could not set to draft this Advance !'),
                    _('Travel is Closed or Cancelled !!!'))
            else:
                self.write({
                    'state': 'draft',
                    'drafted_by': uid,
                    'date_drafted':
                    time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_cancel(self, uid):
        for advance in self.browse(self):
            if advance.travel_id.state in ('closed'):
                raise Warning(
                    _('Could not cancel Advance !'),
                    _('This Advance is already linked to \
                        Travel Expenses record'))
            elif advance.move_id.id:
                move_obj = self.pool.get('account.move')
                move_id = advance.move_id.id
                if not advance.paid:
                    # (move_line.reconcile_id.id or move_line.
                    # reconcile_partial_id.id):
                    if advance.move_id.state == 'posted':
                        move_obj.button_cancel([move_id])
                    self.write(
                        {'move_id': False,
                         'state': 'cancel',
                         'cancelled_by': uid,
                         'date_cancelled':
                         time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
                    move_obj.unlink([move_id])
                else:
                    raise Warning(
                        _('Could not cancel Advance !'),
                        _('This Advance is already paid'))
            else:
                self.write({'move_id': False,
                            'state': 'cancel',
                            'cancelled_by': uid,
                            'date_cancelled':
                            time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_approve(self, uid):
        for advance in self.browse(self):
            if advance.state in ('draft'):
                if advance.total <= 0.0:
                    raise Warning(
                        _('Could not approve Advance !'),
                        _('Total Amount must be greater than zero.'))
                self.write({'state': 'approved',
                            'approved_by': uid,
                            'date_approved':
                            time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_confirm(self):
        adv_invoice = self.pool.get('tms.advance.invoice')
        adv_invoice.makeInvoices(self)
        return True

    def copy(self, default=None):
        default = default or {}
        default.update({
            'cancelled_by': False,
            'date_cancelled': False,
            'approved_by': False,
            'date_approved': False,
            'confirmed_by': False,
            'date_confirmed': False,
            'closed_by': False,
            'date_closed': False,
            'drafted_by': False,
            'date_drafted': False,
            'move_id': False,
            'notes': False,
            'expense_id': False,
            'expense2_id': False,
        })
        return super(TmsAdvance, self).copy(id, default)

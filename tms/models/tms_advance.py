# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

from openerp import fields, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


# Travel - Money advance payments for Travel expenses
class TmsAdvance(models.Model):
    _name = 'tms.advance'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Money advance payments for Travel expenses'

    name = fields.Char('Anticipo', size=64, )
    state = fields.Selection(
        [('draft', 'Draft'), ('approved', 'Approved'),
         ('confirmed', 'Confirmed'), ('closed', 'Closed'),
         ('cancel', 'Cancelled')], 'State', readonly=True,
        default=(lambda *a: 'draft'))
    date = fields.Date(
        'Date',
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]},
        required=True,
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT)))
    travel_id = fields.Many2one(
        'tms.travel', 'Travel',
        required=True,
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]})
    unit_id = fields.Many2one(
        related='travel_id.unit_id', relation='fleet.vehicle',
        string='Unit', readonly=True)
    employee1_id = fields.Many2one(
        related='travel_id.employee_id', relation='hr.employee',
        string='Driver', readonly=True)
    employee2_id = fields.Many2one(
        related='travel_id.employee2_id', relation='hr.employee',
        string='Driver Helper', readonly=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Driver',
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]}, required=True)
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('purchase_ok', '=', 1),
                ('tms_category', '=', 'real_expense')],
        required=True, states={'cancel': [('readonly', True)],
                               'confirmed': [('readonly', True)],
                               'closed': [('readonly', True)]},
        ondelete='restrict')
    product_uom_qty = fields.Float(
        'Quantity', required=True,
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=1)
    product_uom = fields.Many2one(
        'product.uom', 'Unit of Measure ', required=True,
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]})
    price_unit = fields.Float('Price Unit', required=True)
    price_unit_control = fields.Float('Price Unit', readonly=True)
    subtotal = fields.Float(
        # compute=_amount,
        string='Subtotal')
    tax_amount = fields.Float(
        # compute=_amount,
        string='Tax Amount')
    total = fields.Float(
        'Total', required=True,
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
        help="Link to the automatically generated Journal Items.\nThis move "
        "is only for Travel Expense Records with balance < 0.0")
    paid = fields.Boolean(
        # compute=_paid,
        method=True, string='Paid')
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=lambda self: self.env['res.users'].company_id.currency_id.id)
    auto_expense = fields.Boolean(
        'Auto Expense',
        help="Check this if you want this product and amount to be "
        "automatically created when Travel Expense Record is created.",
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]})
    driver_helper = fields.Boolean(
        'For Driver Helper',
        help="Check this if you want to give this advance to "
        "Driver Helper.",
        states={'cancel': [('readonly', True)],
                'approved': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]})
    expense_id = fields.Many2one(
        'tms.expense', 'Expense Record', readonly=True)
    expense2_id = fields.Many2one(
        'tms.expense', 'Expense Record for Drivef Helper',
        readonly=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Advance number must be unique !'),
    ]
    _order = "name desc, date desc"

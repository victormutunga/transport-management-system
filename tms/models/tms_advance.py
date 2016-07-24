# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class TmsAdvance(models.Model):
    _name = 'tms.advance'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Money advance payments for Travel expenses'
    _order = "name desc, date desc"

    base_id = fields.Many2one(
        'tms.base', string='Base', required=True
    )
    name = fields.Char('Advance Number')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('approved', 'Approved'),
         ('confirmed', 'Confirmed'),
         ('closed', 'Closed'),
         ('cancel', 'Cancelled')],
        string='State', readonly=True, default='draft')
    date = fields.Date(
        'Date',
        required=True,
        default=fields.Date.today)
    travel_id = fields.Many2one(
        'tms.travel', 'Travel',
        required=True)
    unit_id = fields.Many2one(
        'fleet.vehicle', related='travel_id.unit_id',
        string='Unit', readonly=True)
    employee_id = fields.Many2one(
        'hr.employee', string='Driver',
        related='travel_id.employee_id',  readonly=True)
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('purchase_ok', '=', 1),
                ('tms_category', '=', 'real_expense')],
        required=True)
    product_uom_qty = fields.Float(
        'Quantity', required=True, default=1.0)
    product_uom_id = fields.Many2one(
        'product.uom', 'Unit of Measure ')
    price_unit = fields.Float('Price Unit', required=True)
    price_unit_control = fields.Float('Price Unit', readonly=True)
    subtotal = fields.Float(
        # compute=_amount,
        string='Subtotal')
    tax_amount = fields.Float(
        # compute=_amount,
        string='Tax Amount')
    total = fields.Float(
        'Total', required=True)
    notes = fields.Text()
    move_id = fields.Many2one(
        'account.move', 'Journal Entry', readonly=True,
        help="Link to the automatically generated Journal Items.\nThis move "
        "is only for Travel Expense Records with balance < 0.0")
    paid = fields.Boolean(
        # compute=_paid
    )
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    auto_expense = fields.Boolean(
        help="Check this if you want this product and amount to be "
        "automatically created when Travel Expense Record is created.")
    expense_id = fields.Many2one(
        'tms.expense', 'Expense Record', readonly=True)
    expense2_id = fields.Many2one(
        'tms.expense', 'Expense Record for Drivef Helper',
        readonly=True)

    @api.model
    def create(self, values):
        advance = super(TmsAdvance, self).create(values)
        sequence = advance.base_id.advance_sequence_id
        advance.name = sequence.next_by_id()
        return advance

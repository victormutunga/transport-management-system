# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


# Travel - Money advance payments for Travel expenses
class TmsAdvance(models.Model):
    _name = 'tms.advance'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Money advance payments for Travel expenses'
    _order = "name desc, date desc"

    base_id = fields.Many2one(
        'tms.base', string='Base'
    )
    name = fields.Char('Anticipo')
    state = fields.Selection(
        [('draft', 'Draft'), ('approved', 'Approved'),
         ('confirmed', 'Confirmed'), ('closed', 'Closed'),
         ('cancel', 'Cancelled')], 'State', readonly=True,
        default='draft')
    date = fields.Date(
        'Date',
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]},
        required=True,
        default=fields.Date.today)
    travel_id = fields.Many2one(
        'tms.travel', 'Travel',
        required=True,
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]})
    unit_id = fields.Many2one(
        related='travel_id.unit_id', relation='fleet.vehicle',
        string='Unit', readonly=True)
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
                               'closed': [('readonly', True)]})
    product_uom_qty = fields.Float(
        'Quantity', required=True,
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=1)
    product_uom_id = fields.Many2one(
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
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]})
    move_id = fields.Many2one(
        'account.move', 'Journal Entry', readonly=True,
        help="Link to the automatically generated Journal Items.\nThis move "
        "is only for Travel Expense Records with balance < 0.0")
    paid = fields.Boolean(
        # compute=_paid
    )
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=lambda self: self.env.user.company_id.currency_id)
    auto_expense = fields.Boolean(
        help="Check this if you want this product and amount to be "
        "automatically created when Travel Expense Record is created.",
        states={'cancel': [('readonly', True)],
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

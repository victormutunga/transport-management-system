# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError


class TmsExpenseLine(models.Model):
    _name = 'tms.expense.line'
    _description = 'Expense Line'

    travel_id = fields.Many2one(
        'tms.travel',
        string='Travel',
        required=True)
    expense_id = fields.Many2one(
        'tms.expense',
        string='Expense',
        readonly=True)
    product_uom_qty = fields.Float(
        string='Qty (UoM)')
    price_unit_control = fields.Float()
    price_subtotal = fields.Float()
    product_uom_id = fields.Many2one(
        'product.uom',
        string='Unit of Measure')
    line_type = fields.Selection(
        [('real_expense', 'Real Expense'),
         ('madeup_expense', 'Made-up Expense'),
         ('salary', 'Salary'),
         ('fuel', 'Fuel'),
         ('salary_retention', 'Salary Retention'),
         ('salary_discount', 'Salary Discount'),
         ('negative_balance', 'Negative Balance')],
        default='real_expense')
    name = fields.Char(
        'Description',
        required=True)
    sequence = fields.Integer(
        help="Gives the sequence order when displaying a list of "
        "sales order lines.",
        default=10)
    price_total = fields.Float(
        string='Total'
        )
    tax_amount = fields.Float()
    special_tax_amount = fields.Float(
        string='Special Tax'
        )
    tax_id = fields.Many2many(
        'account.tax',
        string='Taxes')
    notes = fields.Text()
    employee_id = fields.Many2one(
        'hr.employee',
        string='Driver')
    date = fields.Date(readonly=True)
    state = fields.Char(readonly=True)
    fuel_voucher = fields.Boolean()
    control = fields.Boolean('Control')
    automatic = fields.Boolean(
        help="Check this if you want to create Advances and/or "
        "Fuel Vouchers for this line automatically")
    credit = fields.Boolean(
        help="Check this if you want to create Fuel Vouchers for "
        "this line")
    is_invoice = fields.Boolean(string='Is Invoice?')
    partner_id = fields.Many2one('res.partner', string='Supplier')
    invoice_date = fields.Date('Date')
    invoice_number = fields.Char()
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Supplier Invoice')
    product_id = fields.Many2one(
        'product.product',
        domain=[('type', '=', 'service'),
                ('purchase_ok', '=', 'True')],
        string='Product')

    @api.onchange('product_uom_qty', 'price_total')
    def _onchange_get_total(self):
        for rec in self:
            total = rec.price_total
            percent = rec.product_id.taxes_id.amount
            qty = rec.product_uom_qty
            total_discount = (percent * total) / 100.0
            unit_total = total - total_discount
            subtotal = unit_total * qty
            rec.price_subtotal = subtotal
            rec.tax_amount = total_discount

    @api.model
    def create(self, values):
        expense_line = super(TmsExpenseLine, self).create(values)
        if expense_line.line_type in ('salary_discount', 'negative_balance'):
            if expense_line.price_total > 0:
                raise ValidationError(_('This line type needs a '
                                        'negative value to continue!'))
        return expense_line

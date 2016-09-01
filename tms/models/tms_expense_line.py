# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


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
    line_type = fields.Selection(
        [
            ('real_expense', 'Real Expense'),
            ('madeup_expense', 'Made-up Expense'),
            ('salary', 'Salary'),
            ('salary_retention', 'Salary Retention'),
            ('salary_discount', 'Salary Discount'),
            ('fuel', 'Fuel'),
            ('indirect', 'Indirect'),
            ('negative_balance', 'Negative Balance'), ],
        'Line Type',
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
    base_id = fields.Many2one(
        'tms.base',
        string='Base',
        required=True)
    date = fields.Date(readonly=True)
    state = fields.Char(readonly=True)
    fuel_voucher = fields.Boolean()
    control = fields.Boolean('Control')
    # Useful to mark those lines that must not be deleted for Expense Record
    # (like Fuel from Fuel Voucher, Toll Stations payed without cash
    # (credit card, voucher, etc)
    automatic = fields.Boolean(
        help="Check this if you want to create Advances and/or "
        "Fuel Vouchers for this line automatically")
    credit = fields.Boolean(
        help="Check this if you want to create Fuel Vouchers for "
        "this line")
    # This fields were created to automatically generate the invoices of
    # the expenses
    is_invoice = fields.Boolean(string='Is Invoice?')
    partner_id = fields.Many2one('res.partner', string='Supplier')
    invoice_date = fields.Date('Date')
    invoice_number = fields.Char()
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Supplier Invoice',
        readonly=True)

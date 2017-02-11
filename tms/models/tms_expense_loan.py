# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models


class TmsExpenseLoan(models.Model):
    _name = "tms.expense.loan"
    _description = "Tms Expense Loan"

    name = fields.Char()
    description = fields.Char(required=True)
    date = fields.Datetime(
        default=fields.Datetime.now)
    employee_id = fields.Many2one(
        'hr.employee', 'Driver', required=True)
    expense_line_ids = fields.One2many(
        'tms.expense.line', 'loan_id', 'Expense Line', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('closed', 'Closed'),
        ('cancel', 'Cancelled')])
    discount_method = fields.Selection([
        ('each', 'Each Travel Expense Record'),
        ('weekly', 'Weekly'),
        ('fortnightly', 'Fortnightly'),
        ('monthly', 'Monthly')], required=True)
    discount_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent', 'Loan Percentage'), ], 'Discount Type', required=True)
    notes = fields.Text()
    origin = fields.Char()
    amount = fields.Float(required=True)
    percent_discount = fields.Float()
    fixed_discount = fields.Float()
    balance = fields.Float()
    paid = fields.Boolean()
    product_id = fields.Many2one(
        'product.product', 'Discount Product',
        required=True)

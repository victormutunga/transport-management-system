# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class TmsExpenseLoan(models.Model):
    _name = 'tms.expense.loan'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'TMS Driver Loan Mgmnt'

    name = fields.Char('Name', size=64, select=True, readonly=True)
    description = fields.Char(
        'Description', size=128, select=True, required=True, readonly=True,
        states={'draft': [('readonly', False)],
                'approved': [('readonly', False)]})
    date = fields.Date(
        'Date', required=True, select=True, readonly=True,
        states={'draft': [('readonly', False)],
                'approved': [('readonly', False)]},
        default=fields.Date.today)
    employee_id = fields.Many2one(
        'hr.employee', 'Driver', required=True,
        domain=[('driver', '=', True)])
    expense_line_ids = fields.One2many(
        'tms.expense.line', 'loan_id', 'Expense Line', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('closed', 'Closed'),
        ('cancel', 'Cancelled')], 'State', readonly=True,
        help="State of the Driver Loan. ", select=True,
        default=(lambda *a: 'draft'))
    discount_method = fields.Selection([
        ('each', 'Each Travel Expense Record'),
        ('weekly', 'Weekly'),
        ('fortnightly', 'Fortnightly'),
        ('monthly', 'Monthly'), ], 'Discount Method',
        select=True, required=True)
    discount_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent', 'Loan Percentage'), ], 'Discount Type', readonly=True,
        states={'draft': [('readonly', False)],
                'approved': [('readonly', False)]},
        required=True, select=True)
    notes = fields.Text('Notes')
    origin = fields.Char(
        'Source Document', size=64,
        help="Reference of the document that generated this Expense Record",
        readonly=True, states={'draft': [('readonly', False)],
                               'approved': [('readonly', False)]})
    amount = fields.Float(
        'Amount', digits_compute=dp.get_precision('Sale Price'), required=True,
        readonly=True, states={'draft': [('readonly', False)],
                               'approved': [('readonly', False)]})
    percent_discount = fields.Float(
        'Percent (%)', digits_compute=dp.get_precision('Sale Price'),
        required=False, help="Please set percent as 10.00%",
        readonly=True, states={'draft': [('readonly', False)],
                               'approved': [('readonly', False)]})
    fixed_discount = fields.Float(
        'Fixed Discount', digits_compute=dp.get_precision('Sale Price'),
        required=False, readonly=True,
        states={'draft': [('readonly', False)],
                'approved': [('readonly', False)]})
    balance = fields.Float(
        compute="_compute_balance",
        method=True,
        digits_compute=dp.get_precision('Sale Price'), string='Balance',
        multi=True,
    )
    paid = fields.Boolean(
        method=True, string='Paid', type='boolean',
        multi=True,)
    product_id = fields.Many2one(
        'product.product', 'Discount Product', readonly=True,
        states={'draft': [('readonly', False)],
                'approved': [('readonly', False)]},
        required=True, domain=[
            ('tms_product_category', '=', ('salary_discount'))],
        ondelete='restrict')
    shop_id = fields.Many2one(
        'operating.unit', string='Shop',
        store=True, readonly=True)
    company_id = fields.Many2one(
       'res.company', string='Company', store=True, readonly=True)
    create_uid = fields.Many2one('res.users', 'Created by')
    create_date = fields.Datetime('Creation Date', select=True)
    cancelled_by = fields.Many2one('res.users', 'Cancelled by')
    date_cancelled = fields.Datetime('Date Cancelled')
    approved_by = fields.Many2one('res.users', 'Approved by')
    date_approved = fields.Datetime('Date Approved')
    confirmed_by = fields.Many2one('res.users', 'Confirmed by')
    date_confirmed = fields.Datetime('Date Confirmed')
    closed_by = fields.Many2one('res.users', 'Closed by')
    date_closed = fields.Datetime('Date Closed')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Loan record must be unique !'),
    ]

    @api.multi
    def _compute_balance(self):
        res = {}
        for record in self.browse(self):
            self.execute('select sum(coalesce(price_total, 0.0))::float from \
                tms_expense_line where loan_id = %s' % (record.id))
            data = filter(None, map(lambda x: x[0], self.fetchall())) or [0.0]
            res[record.id] = {
                'balance': record.amount + data[0],
                'paid': not (record.amount + data[0]) > 0,
            }
        return res

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
#############################################################################

import time

from datetime import datetime

from openerp import fields, models
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _

# TMS Travel Expenses


class TmsExpenseLoan(models.Model):
    _name = 'tms.expense.loan'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'TMS Driver Loan Mgmnt'

    def _balance(self, field_name, args):
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

    def _get_loan_discounts_from_expense_lines(self):
        expense_line = {}
        for line in self.pool.get('tms.expense.line').browse(self):
            expense_line[line.loan_id.id] = True

        expense_line_ids = []
        if expense_line:
            expense_line_ids = self.pool.get('tms.expense.loan').search(
                [('id', 'in', expense_line.keys())])
        return expense_line_ids

    name = fields.Char('Name', size=64, select=True, readonly=True)
    description = fields.Char(
        'Description', size=128, select=True, required=True, readonly=True,
        states={'draft': [('readonly', False)],
                'approved': [('readonly', False)]})
    date = fields.Date(
        'Date', required=True, select=True, readonly=True,
        states={'draft': [('readonly', False)],
                'approved': [('readonly', False)]},
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT)))
    employee_id = fields.Many2one(
        'hr.employee', 'Driver', required=True,
        domain=[('tms_category', '=', 'driver')], readonly=True,
        states={'draft': [('readonly', False)],
                'approved': [('readonly', False)]})
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
        ('monthly', 'Monthly'), ], 'Discount Method', readonly=True,
        states={'draft': [('readonly', False)],
                'approved': [('readonly', False)]},
        help="""Select Loan Recovery Method:
- Weekly: Discount will be applied every week, considering only 4 weeks in
    each month
- Fortnightly: Discount will be applied forthnightly, considering only 2
    discounts in each month, applied the 14th and 28th day of the month.
- Monthy: Discount will be applied only once a month, applied the 28th day
    of the month.""", select=True, required=True)
    discount_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent', 'Loan Percentage'), ], 'Discount Type', readonly=True,
        states={'draft': [('readonly', False)],
                'approved': [('readonly', False)]},
        required=True, help="""Select Loan Recovery Type:
- Fixed: Discount will a fixed amount
- Percent: Discount will be a percentage of total Loan Amount""", select=True)
    notes = fields.Text('Notes')
    origin = fields.Char(
        'Source Document', size=64,
        help="Reference of the document that generated this Expense Record",
        readonly=True, states={'draft': [('readonly', False)],
                               'approved': [('readonly', False)]})
    amount = fields.Float(
        'Amount', digits_compute=dp.get_precision('Sale Price'), required=True,
        readonly=True, states={'draft': [('readonly', False)],
                               'approved': [('readonly', False)]}),
    percent_discount = fields.Float(
        'Percent (%)', digits_compute=dp.get_precision('Sale Price'),
        required=False, help="Please set percent as 10.00%",
        readonly=True, states={'draft': [('readonly', False)],
                               'approved': [('readonly', False)]}),
    fixed_discount = fields.Float(
        'Fixed Discount', digits_compute=dp.get_precision('Sale Price'),
        required=False, readonly=True,
        states={'draft': [('readonly', False)],
                'approved': [('readonly', False)]})
    balance = fields.Float(
        compute=_balance, method=True,
        digits_compute=dp.get_precision('Sale Price'), string='Balance',
        multi=True,
        store={
            'tms.expense.loan': (lambda self, cr, uid, ids, c={}: ids,
                                 ['notes', 'amount', 'state',
                                  'expense_line_ids'], 10),
            'tms.expense.line': (_get_loan_discounts_from_expense_lines,
                                 ['product_uom_qty', 'price_unit'], 10),
        })
    # store = {'tms.expense.line': (_get_loan_discounts_from_expense_lines,
    # None, 50)}),
    paid = fields.Boolean(
        compute=_balance, method=True, string='Paid', type='boolean',
        multi=True,
        store={
            'tms.expense.loan': (lambda self, cr, uid, ids, c={}: ids,
                                 ['notes', 'amount', 'state',
                                  'expense_line_ids'], 10),
            'tms.expense.line': (_get_loan_discounts_from_expense_lines,
                                 ['product_uom_qty', 'price_unit'], 10),
        })
    # store = {'tms.expense.line': (_get_loan_discounts_from_expense_lines,
    #       None, 50)}),
    product_id = fields.Many2one(
        'product.product', 'Discount Product', readonly=True,
        states={'draft': [('readonly', False)],
                'approved': [('readonly', False)]},
        required=True, domain=[('tms_category', '=', ('salary_discount'))],
        ondelete='restrict')
    shop_id = fields.Many2one(
        compute='employee_id.shop_id', relation='sale.shop', string='Shop',
        store=True, readonly=True)
    company_id = fields.Many2one(
        compute='shop_id.company_id', type='many2one', relation='res.company',
        string='Company', store=True, readonly=True)
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

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Loan record must be unique !'),
    ]

    def create(self, vals):
        values = vals
        if 'employee_id' in vals and vals['employee_id']:
            employee = self.pool.get('hr.employee').browse(
                [vals['employee_id']])[0]
            seq_id = employee.shop_id.tms_loan_seq.id
            if seq_id:
                seq_number = self.pool.get('ir.sequence').get_id(seq_id)
                values['name'] = seq_number
            else:
                raise Warning(
                    _('Loan Sequence Error !'),
                    _('You have not defined Loan Sequence for shop \
                        ' + employee.shop_id.name))
        return super(TmsExpenseLoan, self).create(values)

    def action_approve(self):
        for rec in self.browse(self):
            if rec.amount <= 0.0:
                raise Warning(
                    _('Could not approve Loan !'),
                    _('Amount must be greater than zero.'))
            self.write({'state': 'approved', 'approved_by': self,
                        'date_approved':
                        time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
            for (id, name) in self.name_get(self):
                message = _("Loan '%s' is set to Approved.") % name
            self.log(id, message)
        return True

    def action_confirm(self):
        for rec in self.browse(self):
            self.write({'state': 'confirmed', 'confirmed_by': self,
                        'date_confirmed':
                        time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
            for (id, name) in self.name_get(self):
                message = _("Loan '%s' is set to Confirmed.") % name
            self.log(id, message)
        return True

    def action_cancel(self):
        for rec in self.browse(self):
            self.write({'state': 'cancel', 'cancelled_by': self,
                        'date_cancelled':
                        time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
            for (id, name) in self.name_get(self):
                message = _("Loan '%s' is set to Cancel.") % name
            self.log(id, message)
        return True

    def action_close(self):
        for rec in self.browse(self):
            self.write({'state': 'closed', 'closed_by': self,
                        'date_closed':
                        time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
            for (id, name) in self.name_get(self):
                message = _(
                    "Loan '%s' is set to Closed even when it is not paid.\
                    ") % name if rec.balance > 0.0 else _(
                    "Loan '%s' is set to Closed.") % name
            self.log(id, message)
        return True

    def get_loan_discounts(self, employee_id, expense_id):
        expense_line_obj = self.pool.get('tms.expense.line')
        expense_obj = self.pool.get('tms.expense')
        res = expense_line_obj.search(
            [('expense_id', '=', expense_id),
             ('control', '=', 1), ('loan_id', '!=', False)])
        # print "res: ", res
        if len(res):
            loan_ids = []
            expense_line_ids = []
            for x in expense_obj.browse([expense_id])[0].expense_line:
                if x.loan_id.id:
                    loan_ids.append(x.loan_id.id)
                    expense_line_ids.append(x.id)
            if len(loan_ids):
                expense_line_obj.unlink(expense_line_ids)
                self.write(loan_ids, {
                    'state': 'confirmed', 'closed_by': False,
                    'date_closed': False})
        prod_obj = self.pool.get('product.product')
        loan_ids = self.search(
            [('employee_id', '=', employee_id),
             ('state', '=', 'confirmed'), ('balance', '>', 0.0)])
        flag_each = True
        fecha_liq = expense_obj.read([expense_id], ['date'])[0]['date']
        for rec in self.browse(loan_ids):
            if rec.discount_method in ('weekly', 'fortnightly', 'monthy'):
                self.execute('select date from tms_expense_line where loan_id \
                    = %s order by date desc limit 1' % (rec.id))
                data = filter(None, map(lambda x: x[0], self.fetchall()))
                date = data[0] if data else rec.date
                # print "fecha_liq: ", fecha_liq
                dur = (datetime.strptime(fecha_liq, '%Y-%m-%d') -
                       datetime.strptime(date, '%Y-%m-%d'))
                product = prod_obj.browse([rec.product_id.id])[0]

                xfactor = (7 if rec.discount_method == 'weekly'
                           else 14.0 if rec.discount_method == 'fortnightly'
                           else 28.0)
                rango = (1 if not int(dur.days / xfactor)
                         else int(dur.days / xfactor) + 1)
                balance = rec.balance
                while rango and balance:
                    rango -= 1
                    discount = (rec.fixed_discount
                                if rec.discount_type == 'fixed'
                                else rec.amount * rec.percent_discount / 100.0)
                    discount = balance if discount > balance else discount
                    balance -= discount
                    xline = {
                        'expense_id': expense_id,
                        'line_type': product.tms_category,
                        'name': product.name + ' - ' + rec.name,
                        'sequence': 100,
                        'product_id': product.id,
                        'product_uom': product.uom_id.id,
                        'product_uom_qty': 1,
                        'price_unit': discount * -1.0,
                        'control': True,
                        'loan_id': rec.id,
                        # 'operation_id': travel.operation_id.id,
                        # 'tax_id': [(6, 0, [x.id for x in
                        # product.supplier_taxes_id])],
                    }
                    res = expense_line_obj.create(xline)
                    if discount >= rec.balance:
                        self.write([rec.id], {
                            'state': 'closed', 'closed_by': self,
                            'date_closed':
                            time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
                        for (id, name) in self.name_get([rec.id]):
                            message = _(
                                "Loan '%s' has been Closed.") % rec.name
                        self.log(id, message)
            elif rec.discount_method == 'each' and flag_each:
                # Buscaoms el ultimo descuento de prestamo de tipo
                # "En cada liquidacion"
                self.execute("""select date from tms_expense_line where
                    loan_id in (select id from tms_expense_loan where
                    employee_id=%s and discount_method='each' and state in
                    ('closed','confirmed')) order by date desc limit 1;
                """ % (rec.employee_id.id))
                data = filter(None, map(lambda x: x[0], self.fetchall()))
                date = data and data[0] or rec.date
                if date >= fecha_liq:
                    continue
                flag_each = False
                self.execute('select date from tms_expense_line where loan_id \
                    = %s order by date desc limit 1' % (rec.id))
                data = filter(None, map(lambda x: x[0], self.fetchall()))
                date = data[0] if data else rec.date
                # print "fecha_liq: ", fecha_liq
                dur = (datetime.strptime(fecha_liq, '%Y-%m-%d') -
                       datetime.strptime(date, '%Y-%m-%d'))
                product = prod_obj.browse([rec.product_id.id])[0]
                balance = rec.balance
                if rec.discount_type == 'fixed':
                    discount = rec.fixed_discount
                else:
                    discount = rec.amount * rec.percent_discount / 100.0
                discount = balance if discount > balance else discount
                balance -= discount
                xline = {
                    'expense_id': expense_id,
                    'line_type': product.tms_category,
                    'name': product.name + ' - ' + rec.name,
                    'sequence': 100,
                    'product_id': product.id,
                    'product_uom': product.uom_id.id,
                    'product_uom_qty': 1,
                    'price_unit': discount * -1.0,
                    'control': True,
                    'loan_id': rec.id,
                    # 'operation_id': travel.operation_id.id,
                    # 'tax_id': [(6, 0, [x.id for x in
                    # product.supplier_taxes_id])],
                }
                res = expense_line_obj.create(xline)
                if discount >= rec.balance:
                    self.write([rec.id], {
                        'state': 'closed',
                        'closed_by': self,
                        'date_closed':
                        time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
                    for (id, name) in self.name_get([rec.id]):
                        message = _("Loan '%s' has been Closed.") % rec.name
                    self.log(id, message)
        return

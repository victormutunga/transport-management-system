# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import _, api, fields, models


class TmsExpenseLoan(models.Model):
    _name = "tms.expense.loan"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Tms Expense Loan"

    operating_unit_id = fields.Many2one(
        'operating.unit', string='Operating Unit', required=True)
    name = fields.Char()
    description = fields.Char(required=True)
    date = fields.Datetime(
        default=fields.Datetime.now)
    employee_id = fields.Many2one(
        'hr.employee', 'Driver', required=True)
    expense_line_ids = fields.One2many(
        'tms.expense.line', 'loan_id', 'Expense Line', readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('authorized', 'Waiting for authorization'),
         ('approved', 'Approved'),
         ('confirmed', 'Confirmed'),
         ('closed', 'Closed'),
         ('cancel', 'Cancelled'), ],
        string='State',
        readonly=True,
        default='draft')
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

    @api.model
    def create(self, values):
        loan = super(TmsExpenseLoan, self).create(values)
        sequence = loan.operating_unit_id.loan_sequence_id
        loan.name = sequence.next_by_id()
        return loan

    @api.multi
    def action_authorized(self):
        for rec in self:
            rec.state = 'approved'

    @api.multi
    def action_approve(self):
        for rec in self:
            if rec.amount > rec.operating_unit_id.credit_limit:
                rec.state = "authorized"
            else:
                rec.state = 'approved'
                rec.message_post(_(
                    '<strong>Loan approved.</strong><ul>'
                    '<li><strong>Approved by: </strong>%s</li>'
                    '<li><strong>Approved at: </strong>%s</li>'
                    '</ul>') % (rec.env.user.name, fields.Datetime.now()))

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
            rec.message_post(_(
                '<strong>Loan cancelled.</strong><ul>'
                '<li><strong>Cancelled by: </strong>%s</li>'
                '<li><strong>Cancelled at: </strong>%s</li>'
                '</ul>') % (self.env.user.name, fields.Datetime.now()))

    @api.multi
    def action_confirm(self):
        for advance in self:
            advance.write(
                {
                    'state': 'confirmed'
                })
            advance.message_post(_(
                '<strong>Loan confirmed.</strong><ul>'
                '<li><strong>Confirmed by: </strong>%s</li>'
                '<li><strong>Confirmed at: </strong>%s</li>'
                '</ul>') % (self.env.user.name,
                            fields.Datetime.now()))

    @api.multi
    def action_cancel_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec.message_post(_(
                '<strong>Loan drafted.</strong><ul>'
                '<li><strong>Drafted by: </strong>%s</li>'
                '<li><strong>Drafted at: </strong>%s</li>'
                '</ul>') % (self.env.user.name, fields.Datetime.now()))

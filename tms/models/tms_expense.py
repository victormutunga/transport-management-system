# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from __future__ import division
import datetime
from openerp import _, api, fields, models
from openerp.exceptions import ValidationError


class TmsExpense(models.Model):
    _name = 'tms.expense'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Travel Expenses'
    _order = 'name desc'

    name = fields.Char(readonly=True)
    operating_unit_id = fields.Many2one(
        'operating.unit', required=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Driver', required=True)
    travel_ids = fields.Many2many(
        'tms.travel',
        string='Travels')
    unit_id = fields.Many2one(
        'fleet.vehicle', 'Unit', required=True)
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled')], 'Expense State', readonly=True,
        help="Gives the state of the Travel Expense. ",
        default='draft')
    date = fields.Date(required=True,
        default=fields.Date.today)
    expense_line_ids = fields.One2many(
        'tms.expense.line', 'expense_id', 'Expense Lines')
    amount_real_expense = fields.Float(
        compute='_compute_amount_real_expense',
        string='Expenses',
        store=True)
    amount_made_up_expense = fields.Float(
        compute='_compute_amount_made_up_expense',
        string='Fake Expenses',
        store=True)
    fuel_qty = fields.Float(
        compute='_compute_fuel_qty',
        store=True)
    amount_fuel = fields.Float(
        compute='_compute_amount_fuel',
        string='Cost of Fuel',
        store=True)
    amount_fuel_cash = fields.Float(
        compute='_compute_amount_fuel_cash',
        string='Fuel in Cash',
        store=True)
    amount_refund = fields.Float(
        compute='_compute_amount_refund',
        string='Refund',
        store=True)
    amount_other_income = fields.Float(
        compute='_compute_amount_other_income',
        string='Other Income',
        store=True)
    amount_salary = fields.Float(
        compute='_compute_amount_salary',
        string='Salary',
        store=True)
    amount_net_salary = fields.Float(
        compute='_compute_amount_net_salary',
        string='Net Salary',
        store=True)
    amount_salary_retention = fields.Float(
        compute='_compute_amount_salary_retention',
        string='Salary Retentions',
        store=True)
    amount_salary_discount = fields.Float(
        compute='_compute_amount_salary_discount',
        string='Salary Discounts',
        store=True)
    amount_advance = fields.Float(
        compute='_compute_amount_advance',
        string='Advances',
        store=True)
    amount_balance = fields.Float(
        compute='_compute_amount_balance',
        string='Balance',
        store=True)
    amount_balance2 = fields.Float(
        compute='_compute_amount_balance2',
        string='Balance',
        store=True)
    amount_tax_total = fields.Float(
        compute='_compute_amount_tax_total',
        string='Taxes (All)',
        store=True)
    amount_tax_real = fields.Float(
        compute='_compute_amount_tax_real',
        string='Taxes (Real)',
        store=True)
    amount_total_real = fields.Float(
        compute='_compute_amount_total_real',
        string='Total (Real)',
        store=True)
    amount_total_total = fields.Float(
        compute='_compute_amount_total_total',
        string='Total (All)',
        store=True)
    amount_subtotal_real = fields.Float(
        compute='_compute_amount_subtotal_real',
        string='SubTotal (Real)',
        store=True)
    amount_subtotal_total = fields.Float(
        string='SubTotal (All)',
        compute='_compute_amount_subtotal_total',
        store=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    last_odometer = fields.Float('Last Read')
    vehicle_odometer = fields.Float()
    current_odometer = fields.Float(
        string='Current Real',
        compute='_compute_current_odometer')
    odometer_log_id = fields.Many2one(
        'fleet.vehicle.odometer', 'Odometer Record')
    notes = fields.Text()
    move_id = fields.Many2one(
        'account.move', 'Journal Entry', readonly=True,
        help="Link to the automatically generated Journal Items.")
    paid = fields.Boolean(
        compute='_compute_paid',
        store=True,
        readonly=True)
    advance_ids = fields.One2many(
        'tms.advance', 'expense_id', string='Advances', readonly=True)
    fuel_qty_real = fields.Float(
        help="Fuel Qty computed based on Distance Real and Global Fuel "
        "Efficiency Real obtained by electronic reading and/or GPS")
    fuel_diff = fields.Float(
        string="Fuel Difference",
        help="Fuel Qty Difference between Fuel Vouchers + Fuel Paid in Cash "
        "versus Fuel qty computed based on Distance Real and Global Fuel "
        "Efficiency Real obtained by electronic reading and/or GPS"
        # compute=_get_fuel_diff
    )
    fuel_log_ids = fields.One2many(
        'fleet.vehicle.log.fuel', 'expense_id', string='Fuel Vouchers')
    start_date = fields.Datetime()
    end_date = fields.Datetime()
    fuel_efficiency = fields.Float(
        readonly=True,
        compute="_compute_fuel_efficiency")
    payment_move_id = fields.Many2one(
        'account.move', string='Payment Entry', readonly=True)
    travel_days = fields.Char(
        compute='_compute_travel_days',
    )
    distance_loaded = fields.Float(
        compute='_compute_distance_expense',
    )
    distance_empty = fields.Float(
        compute='_compute_distance_expense',
    )
    distance_loaded_real = fields.Float()
    distance_empty_real = fields.Float()
    distance_routes = fields.Float(
        compute='_compute_distance_routes',
        string='Distance from routes',
        help="Routes Distance")
    distance_real = fields.Float(
        help="Route obtained by electronic reading and/or GPS")
    income_km = fields.Float(
        compute='_compute_income_km',
    )
    expense_km = fields.Float(
        compute='_compute_expense_km',
    )
    percentage_km = fields.Float(
        'Productivity Percentage',
        compute='_compute_percentage_km',
    )
    fuel_efficiency_real = fields.Float(
    )

    @api.depends('travel_ids')
    def _compute_income_km(self):
        for rec in self:
            rec.income_km = 0.0
            rec.expense = 0.0
            subtotal_waybills = 0.0
            for travel in rec.travel_ids:
                for waybill in travel.waybill_ids:
                    subtotal_waybills += waybill.amount_untaxed
            try:
                rec.income_km = subtotal_waybills / rec.distance_real
            except ZeroDivisionError:
                rec.income_km = 0.0

    @api.depends('distance_real', 'amount_subtotal_real')
    def _compute_expense_km(self):
        for rec in self:
            try:
                rec.expense_km = rec.amount_subtotal_real / rec.distance_real
            except ZeroDivisionError:
                rec.expense_km = 0.0

    @api.depends('income_km', 'expense_km')
    def _compute_percentage_km(self):
        for rec in self:
            try:
                rec.percentage_km = rec.income_km / rec.expense_km
            except ZeroDivisionError:
                rec.percentage_km = 0.0

    @api.depends('travel_ids')
    def _compute_distance_expense(self):
        for rec in self:
            for travel in rec.travel_ids:
                rec.distance_loaded += travel.distance_loaded
                rec.distance_empty += travel.distance_empty

    @api.depends('start_date', 'end_date')
    def _compute_travel_days(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                strp_start_date = datetime.datetime.strptime(
                    rec.start_date, "%Y-%m-%d %H:%M:%S")
                strp_end_date = datetime.datetime.strptime(
                    rec.end_date, "%Y-%m-%d %H:%M:%S")
                difference = strp_end_date - strp_start_date
                hours = int(difference.seconds / 3600)
                mins = int((difference.seconds - (hours * 3600))/60)
                seconds = difference.seconds - ((hours * 3600) + (mins * 60))
                if hours < 10:
                    hours = '0' + str(hours)
                if mins < 10:
                    mins = '0' + str(mins)
                if seconds < 10:
                    seconds = '0' + str(seconds)
                total_string = (
                    str(difference.days) + _('Day(s), ') +
                    str(hours) + ':' +
                    str(mins) + ':' +
                    str(seconds))
                rec.travel_days = total_string

    @api.depends('payment_move_id')
    def _compute_paid(self):
        for rec in self:
            if rec.payment_move_id:
                rec.paid = True

    @api.depends('fuel_qty', 'distance_real')
    def _compute_fuel_efficiency(self):
        for rec in self:
            if rec.distance_real and rec.fuel_qty:
                rec.fuel_efficiency = rec.distance_real / rec.fuel_qty

    @api.depends('expense_line_ids')
    def _compute_fuel_qty(self):
        for rec in self:
            for line in rec.expense_line_ids:
                if line.line_type == 'fuel':
                    rec.fuel_qty += line.product_qty

    @api.depends('travel_ids', 'expense_line_ids')
    def _compute_amount_fuel(self):
        for rec in self:
            rec.amount_fuel = 0.0
            for line in rec.fuel_log_ids:
                rec.amount_fuel += (
                    line.price_subtotal +
                    line.special_tax_amount)

    @api.depends('expense_line_ids')
    def _compute_amount_fuel_cash(self):
        for rec in self:
            rec.amount_fuel_cash = 0.0
            for line in rec.expense_line_ids:
                if line.line_type == 'fuel_cash':
                    rec.amount_fuel_cash += (
                        line.price_subtotal +
                        line.special_tax_amount)

    @api.depends('expense_line_ids')
    def _compute_amount_refund(self):
        for rec in self:
            rec.amount_refund = 0.0
            for line in rec.expense_line_ids:
                if line.line_type == 'refund':
                    rec.amount_refund += line.price_total

    @api.depends('expense_line_ids')
    def _compute_amount_other_income(self):
        for rec in self:
            rec.amount_other_income = 0.0
            for line in rec.expense_line_ids:
                if line.line_type == 'other_income':
                    rec.amount_other_income += line.price_total

    @api.depends('expense_line_ids')
    def _compute_amount_salary(self):
        for rec in self:
            rec.amount_salary = 0.0
            for line in rec.expense_line_ids:
                if line.line_type == 'salary':
                    rec.amount_salary += line.price_total

    @api.depends('expense_line_ids')
    def _compute_amount_salary_discount(self):
        for rec in self:
            rec.amount_salary_discount = 0
            for line in rec.expense_line_ids:
                if line.line_type == 'salary_discount':
                    rec.amount_salary_discount += line.price_total

    @api.depends('expense_line_ids')
    def _compute_amount_made_up_expense(self):
        for rec in self:
            rec.amount_made_up_expense = 0
            for line in rec.expense_line_ids:
                if line.line_type == 'made_up_expense':
                    rec.amount_made_up_expense += line.price_total

    @api.depends('expense_line_ids')
    def _compute_amount_real_expense(self):
        for rec in self:
            rec.amount_real_expense = 0
            for line in rec.expense_line_ids:
                if line.line_type == 'real_expense':
                    rec.amount_real_expense += line.price_subtotal

    @api.depends('travel_ids', 'expense_line_ids')
    def _compute_amount_subtotal_real(self):
        for rec in self:
            rec.amount_subtotal_real = (
                rec.amount_salary +
                rec.amount_salary_discount +
                rec.amount_real_expense +
                rec.amount_salary_retention +
                rec.amount_refund +
                rec.amount_fuel_cash +
                rec.amount_other_income)

    @api.depends('travel_ids', 'expense_line_ids')
    def _compute_amount_total_real(self):
        for rec in self:
            rec.amount_total_real = (
                rec.amount_subtotal_real +
                rec.amount_tax_real)

    @api.depends('travel_ids', 'expense_line_ids')
    def _compute_amount_balance(self):
        for rec in self:
            rec.amount_balance = (rec.amount_total_real -
                                  rec.amount_advance)

    @api.depends('travel_ids')
    def _compute_amount_net_salary(self):
        for rec in self:
            rec.amount_net_salary = 1.0

    @api.depends('expense_line_ids')
    def _compute_amount_salary_retention(self):
        for rec in self:
            for line in rec.expense_line_ids:
                if line.line_type == 'salary_retention':
                    rec.amount_salary_retention += line.price_total

    @api.depends('travel_ids', 'expense_line_ids')
    def _compute_amount_advance(self):
        for rec in self:
            rec.amount_advance = 0
            for travel in rec.travel_ids:
                for advance in travel.advance_ids:
                    if advance.payment_move_id:
                        rec.amount_advance += advance.amount

    @api.depends('travel_ids')
    def _compute_amount_balance2(self):
        for rec in self:
            rec.amount_balance2 = 1.0

    @api.depends('travel_ids', 'expense_line_ids')
    def _compute_amount_tax_total(self):
        for rec in self:
            rec.amount_tax_total = 0
            for travel in rec.travel_ids:
                for fuel_log in travel.fuel_log_ids:
                    rec.amount_tax_total += fuel_log.tax_amount
            rec.amount_tax_total += rec.amount_tax_real

    @api.depends('expense_line_ids')
    def _compute_amount_tax_real(self):
        for rec in self:
            rec.amount_tax_real = 0
            for line in rec.expense_line_ids:
                if line.line_type == 'real_expense':
                    rec.amount_tax_real += line.tax_amount

    @api.depends('travel_ids', 'expense_line_ids')
    def _compute_amount_subtotal_total(self):
        for rec in self:
            rec.amount_subtotal_total = 0
            for travel in rec.travel_ids:
                for fuel_log in travel.fuel_log_ids:
                    rec.amount_subtotal_total += (
                        fuel_log.price_subtotal +
                        fuel_log.special_tax_amount)
            for line in rec.expense_line_ids:
                if line.line_type == 'real_expense':
                    rec.amount_subtotal_total += line.price_subtotal
            rec.amount_subtotal_total += rec.amount_balance

    @api.depends('travel_ids', 'expense_line_ids')
    def _compute_amount_total_total(self):
        for rec in self:
            rec.amount_total_total = (
                rec.amount_subtotal_total + rec.amount_tax_total +
                rec.amount_made_up_expense)

    @api.depends('travel_ids')
    def _compute_distance_routes(self):
        distance = 0.0
        for rec in self:
            for travel in rec.travel_ids:
                distance += travel.route_id.distance
            rec.distance_routes = distance

    @api.depends('travel_ids')
    def _compute_current_odometer(self):
        for rec in self:
            rec.current_odometer = rec.unit_id.odometer

    @api.model
    def create(self, values):
        expense = super(TmsExpense, self).create(values)
        sequence = expense.operating_unit_id.expense_sequence_id
        expense.name = sequence.next_by_id()
        return expense

    @api.multi
    def write(self, values):
        for rec in self:
            res = super(TmsExpense, self).write(values)
            rec.get_travel_info()
            return res

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'confirmed':
                raise ValidationError(
                    _('You can not delete a travel expense'
                      'in status confirmed'))
            else:
                travels = self.env['tms.travel'].search(
                    [('expense_id', '=', rec.id)])
                travels.write({
                    'expense_id': False,
                    'state': 'done'
                })
                advances = self.env['tms.advance'].search(
                    [('expense_id', '=', rec.id)])
                advances.write({
                    'expense_id': False,
                    'state': 'confirmed'
                })
                fuel_logs = self.env['fleet.vehicle.log.fuel'].search(
                    [('expense_id', '=', rec.id)])
                fuel_logs.write({
                    'expense_id': False,
                    'state': 'confirmed'
                })
                return super(TmsExpense, self).unlink()

    @api.multi
    def action_approved(self):
        for rec in self:
            message = _('<b>Expense Approved.</b></br><ul>'
                        '<li><b>Approved by: </b>%s</li>'
                        '<li><b>Approved at: </b>%s</li>'
                        '</ul>') % (
                            self.env.user.name,
                            fields.Date.today())
            rec.message_post(body=message)
        self.state = 'approved'

    @api.multi
    def action_draft(self):
        for rec in self:
            message = _('<b>Expense Drafted.</b></br><ul>'
                        '<li><b>Drafted by: </b>%s</li>'
                        '<li><b>Drafted at: </b>%s</li>'
                        '</ul>') % (
                            self.env.user.name,
                            fields.Date.today())
            rec.message_post(body=message)
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        for rec in self:
            move_obj = self.env['account.move']
            journal_id = rec.operating_unit_id.expense_journal_id.id
            advance_account_id = (
                rec.employee_id.
                tms_advance_account_id.id
            )
            negative_account = (
                rec.employee_id.
                tms_expense_negative_account_id.id
            )
            driver_account_payable = (
                rec.employee_id.
                address_home_id.property_account_payable_id.id
            )
            if not journal_id:
                raise ValidationError(
                    _('Warning! The expense does not have a journal'
                      ' assigned. \nCheck if you already set the '
                      'journal for expense moves in the Operating Unit.'))
            if not driver_account_payable:
                raise ValidationError(
                    _('Warning! The driver does not have a home address'
                      ' assigned. \nCheck if you already set the '
                      'home address for the employee.'))
            if not advance_account_id:
                raise ValidationError(
                    _('Warning! You must have configured the accounts'
                        'of the tms for the Driver'))
            move_lines = []
            # We check if the advance amount is higher than zero to create
            # a move line
            if rec.amount_advance > 0:
                move_line = (0, 0, {
                    'name': _('Advance Discount'),
                    'ref': (rec.name),
                    'account_id': advance_account_id,
                    'narration': rec.name,
                    'debit': 0.0,
                    'credit': rec.amount_advance,
                    'journal_id': journal_id,
                    'partner_id': rec.employee_id.address_home_id.id,
                    'operating_unit_id': rec.operating_unit_id.id,
                })
                move_lines.append(move_line)
            invoices = []

            for line in rec.expense_line_ids:
                if line.line_type == 'fuel' and not line.control:
                    self.env['fleet.vehicle.log.fuel'].create({
                        'operating_unit_id': rec.operating_unit_id.id,
                        'travel_id': line.travel_id.id,
                        'vehicle_id': line.travel_id.unit_id.id,
                        'product_id': line.product_id.id,
                        'price_unit': line.unit_price,
                        'price_subtotal': line.price_subtotal,
                        'vendor_id': line.partner_id.id,
                        'product_qty': line.product_qty,
                        'tax_amount': line.tax_amount,
                        'state': 'closed',
                        'employee_id':  rec.employee_id.id,
                        'price_total': line.price_total,
                        'date': str(fields.Date.today()),
                        'expense_control': True,
                        'expense_id': rec.id,
                        'ticket_number': line.invoice_number,
                        })
                    line.control = True
                # We only need all the lines except the fuel and the
                # made up expenses
                if line.line_type not in ('made_up_expense', 'fuel'):
                    product_account = (
                        negative_account
                        if (line.product_id.
                            tms_product_category == 'negative_balance')
                        else (line.product_id.
                              property_account_expense_id.id)
                        if (line.product_id.
                            property_account_expense_id.id)
                        else (line.product_id.categ_id.
                              property_account_expense_categ_id.id)
                        if (line.product_id.categ_id.
                            property_account_expense_categ_id.id)
                        else False)
                    if not product_account:
                        raise ValidationError(
                            _('Warning ! Expense Account is not defined for'
                                ' product %s') % (line.product_id.name))
                    inv_id = False
                    # We check if the expense line is an invoice to create it
                    # and make the move line based in the total with taxes
                    if line.is_invoice:
                        inv_id = self.create_supplier_invoice(line)
                        inv_id.signal_workflow('invoice_open')
                        invoices.append(inv_id)
                        move_line = (0, 0, {
                            'name': (
                                rec.name + ' ' + line.name +
                                ' - Inv ID - ' + str(inv_id.id)),
                            'ref': (
                                rec.name + ' - Inv ID - ' + str(inv_id.id)),
                            'account_id': (
                                line.partner_id.
                                property_account_payable_id.id),
                            'debit': (
                                line.price_total if line.price_total > 0.0
                                else 0.0),
                            'credit': (
                                line.price_total if line.price_total <= 0.0
                                else 0.0),
                            'journal_id': journal_id,
                            'partner_id': line.partner_id.id,
                            'operating_unit_id': rec.operating_unit_id.id,
                        })
                        move_lines.append(move_line)
                    # if the expense line not be a invoice we make the move
                    # line based in the subtotal
                    else:
                        move_line = (0, 0, {
                            'name': rec.name + ' ' + line.name,
                            'ref': rec.name,
                            'account_id': product_account,
                            'debit': (
                                line.price_subtotal
                                if line.price_subtotal > 0.0
                                else 0.0),
                            'credit': (
                                line.price_subtotal * - 1.0
                                if line.price_subtotal <= 0.0
                                else 0.0),
                            'journal_id': journal_id,
                            'partner_id': rec.employee_id.address_home_id.id,
                            'operating_unit_id': rec.operating_unit_id.id,
                        })
                        move_lines.append(move_line)
                    # we check the line tax to create the move line if
                    # the line not be an invoice
                    for tax in line.tax_ids:
                        tax_account = tax.account_id.id
                        if not tax_account:
                            raise ValidationError(
                                _('Warning !'),
                                _('Tax Account is not defined for '
                                  'Tax %s (id:%d)') % (tax.name, tax.id,))
                        tax_amount = line.tax_amount
                        # We create a move line for the line tax
                        if not line.is_invoice:
                            move_line = (0, 0, {
                                'name': (rec.name + ' ' + line.name),
                                'ref': rec.name,
                                'account_id': tax_account,
                                'debit': (
                                    tax_amount if tax_amount > 0.0
                                    else 0.0),
                                'credit': (
                                    tax_amount if tax_amount <= 0.0
                                    else 0.0),
                                'journal_id': journal_id,
                                'partner_id': (
                                    rec.employee_id.address_home_id.id),
                                'operating_unit_id': rec.operating_unit_id.id,
                            })
                            move_lines.append(move_line)
            # Here we check if the balance is positive or negative to create
            # the move line with the correct values
            if rec.amount_balance < 0:
                move_line = (0, 0, {
                    'name': _('Negative Balance'),
                    'ref': rec.name,
                    'account_id': negative_account,
                    'debit': rec.amount_balance * -1.0,
                    'credit': 0.0,
                    'journal_id': journal_id,
                    'partner_id':
                    rec.employee_id.address_home_id.id,
                    'operating_unit_id': rec.operating_unit_id.id,
                })
                move_lines.append(move_line)
            else:
                move_line = (0, 0, {
                    'name': rec.name,
                    'account_id': driver_account_payable,
                    'debit': 0.0,
                    'credit': rec.amount_balance,
                    'journal_id': journal_id,
                    'partner_id':
                    rec.employee_id.address_home_id.id,
                    'operating_unit_id': rec.operating_unit_id.id,
                })
                move_lines.append(move_line)
            move = {
                'date': fields.Date.today(),
                'journal_id': journal_id,
                'name': rec.name,
                'line_ids': [line for line in move_lines],
                'partner_id': self.env.user.company_id.id,
                'operating_unit_id': rec.operating_unit_id.id,
            }
            move_id = move_obj.create(move)
            if not move_id:
                raise ValidationError(
                    _('An error has occurred in the creation'
                        ' of the accounting move. '))
            move_id.post()
            # Here we reconcile the invoices with the corresponding
            # move line
            self.reconcile_supplier_invoices(invoices, move_id)
            rec.write(
                {
                    'move_id': move_id.id,
                    'state': 'confirmed'
                })
            message = _('<b>Expense Confirmed.</b></br><ul>'
                        '<li><b>Confirmed by: </b>%s</li>'
                        '<li><b>Confirmed at: </b>%s</li>'
                        '</ul>') % (
                            self.env.user.name,
                            fields.Date.today())
            rec.message_post(body=message)

    @api.multi
    def action_cancel(self):
        if self.paid:
            raise ValidationError(
                _('You cannot cancel an expense that is paid.'))
        if self.state == 'confirmed':
            for line in self.expense_line_ids:
                if line.invoice_id and line.line_type != 'fuel':
                    for move_line in line.invoice_id.move_id.line_ids:
                        if move_line.account_id.reconcile:
                            move_line.remove_move_reconcile()
                    line.invoice_id.write({
                        # TODO Make a separate module to delete oml data
                        'cfdi_fiscal_folio': False,
                        'xml_signed': False,
                        'reference': False,
                        })
                    line.invoice_id.signal_workflow('invoice_cancel')
                    line.invoice_id = False
            if self.move_id.state == 'posted':
                self.move_id.button_cancel()
            self.move_id.unlink()
        self.state = 'cancel'

    @api.multi
    def get_travel_info(self):
        for rec in self:
            exp_no_travel = rec.expense_line_ids.search([
                ('expense_id', '=', rec.id),
                ('travel_id', '=', False)]).ids
            rec.expense_line_ids.search([
                ('expense_id', '=', rec.id),
                ('travel_id', 'not in', rec.travel_ids.ids),
                ('id', 'not in', exp_no_travel)]).unlink()
            rec.expense_line_ids.search([
                ('expense_id', '=', rec.id),
                ('control', '=', True)]).unlink()
            travels = self.env['tms.travel'].search(
                [('expense_id', '=', rec.id)])
            travels.write({'expense_id': False, 'state': 'done'})
            advances = self.env['tms.advance'].search(
                [('expense_id', '=', rec.id)])
            for adv in advances:
                if adv.state != 'cancel':
                    adv.state = 'confirmed'
                adv.expense_id = False
            fuel_logs = self.env['fleet.vehicle.log.fuel'].search(
                [('expense_id', '=', rec.id)])
            fuel_logs.write({
                'expense_id': False,
                'state': 'confirmed'
            })
            for travel in rec.travel_ids:
                travel.write({'state': 'closed', 'expense_id': rec.id})
                for advance in travel.advance_ids:
                    if advance.state not in ('confirmed', 'cancel'):
                        raise ValidationError(_(
                            'Oops! All the advances must be confirmed'
                            ' or cancelled \n '
                            'Name of advance not confirmed or cancelled: ' +
                            advance.name +
                            '\n State: ' + advance.state))
                    if not advance.paid:
                        if advance.move_id.matched_percentage == 1.0:
                            advance_move = advance.move_id.line_ids[-1]
                            if advance_move.credit > 0:
                                move_lines = advance.move_id.line_ids[-1]
                                reconcile_move = move_lines.full_reconcile_id
                                for line in reconcile_move.reconciled_line_ids:
                                    if line.journal_id.type == 'bank':
                                        move_id = line.move_id.id
                            advance.write(
                                {'paid': True, 'payment_move_id': move_id})
                    if not advance.paid and advance.state == 'confirmed':
                        raise ValidationError(_(
                            'Oops! All the advances must be paid'
                            '\n Name of advance not paid: ' +
                            advance.name))
                    if (advance.auto_expense and
                            advance.state == 'confirmed'):
                        rec.expense_line_ids.create({
                            'name': _("Advance: ") + str(advance.name),
                            'travel_id': travel.id,
                            'expense_id': rec.id,
                            'line_type': "real_expense",
                            'product_id': advance.product_id.id,
                            'product_qty': 1.0,
                            'unit_price': advance.amount,
                            'control': True
                        })
                    if advance.state != 'cancel':
                        advance.write({
                            'state': 'closed',
                            'expense_id': rec.id
                        })
                for fuel_log in travel.fuel_log_ids:
                    if (fuel_log.state != 'confirmed' and
                            fuel_log.state != 'closed'):
                        raise ValidationError(_(
                            'Oops! All the voucher must be confirmed'
                            '\n Name of voucher not confirmed: ' +
                            fuel_log.name +
                            '\n State: ' + fuel_log.state))
                    else:
                        if not fuel_log.expense_control:
                            rec.expense_line_ids.create({
                                'name': _(
                                    "Fuel voucher: ") + str(fuel_log.name),
                                'travel_id': travel.id,
                                'expense_id': rec.id,
                                'line_type': 'fuel',
                                'product_id': fuel_log.product_id.id,
                                'product_qty': fuel_log.product_qty,
                                'product_uom_id': (
                                    fuel_log.product_id.uom_id.id),
                                'unit_price': fuel_log.price_total,
                                'is_invoice': fuel_log.invoice_paid,
                                'invoice_id': fuel_log.invoice_id.id,
                                'control': True,
                            })
                        fuel_log.write({
                            'state': 'closed',
                            'expense_id': rec.id
                        })
                product_id = self.env['product.product'].search(
                    [('tms_product_category', '=', 'salary')])
                if not product_id:
                    raise ValidationError(_(
                        'Oops! You must create a product for the'
                        ' diver salary with the Salary TMS '
                        'Product Category'))
                rec.expense_line_ids.create({
                    'name': _("Salary per travel: ") + str(travel.name),
                    'travel_id': travel.id,
                    'expense_id': rec.id,
                    'line_type': "salary",
                    'product_qty': 1.0,
                    'product_uom_id': product_id.uom_id.id,
                    'product_id': product_id.id,
                    'unit_price': rec.get_driver_salary(travel),
                    'control': True
                })

    @api.depends('travel_ids')
    def get_driver_salary(self, travel):
        for rec in self:
            driver_salary = 0.0
            for waybill in travel.waybill_ids:
                income = 0.0
                for line in waybill.waybill_line_ids:
                    if line.product_id.apply_for_salary:
                        income += line.price_subtotal
                if waybill.currency_id.name == 'USD':
                    income = (income *
                              self.env.user.company_id.expense_currency_rate)
                if waybill.driver_factor_ids:
                    for factor in waybill.driver_factor_ids:
                        driver_salary += factor.get_amount(
                            weight=waybill.product_weight,
                            distance=waybill.distance_route,
                            distance_real=waybill.distance_real,
                            qty=waybill.product_qty,
                            volume=waybill.product_volume,
                            income=income,
                            employee=rec.employee_id)
                elif travel.driver_factor_ids:
                    for factor in travel.driver_factor_ids:
                        driver_salary += factor.get_amount(
                            weight=waybill.product_weight,
                            distance=waybill.distance_route,
                            distance_real=waybill.distance_real,
                            qty=waybill.product_qty,
                            volume=waybill.product_volume,
                            income=income,
                            employee=rec.employee_id)
                else:
                    raise ValidationError(_(
                        'Oops! You have not defined a Driver factor in '
                        'the Travel or the Waybill\nTravel: %s' %
                        travel.name))
            return driver_salary

    @api.multi
    def create_supplier_invoice(self, line):
        journal_id = self.operating_unit_id.expense_journal_id.id
        product_account = (
            line.product_id.product_tmpl_id.property_account_expense_id.id)
        if not product_account:
            product_account = (
                line.product_id.categ_id.property_account_expense_categ_id.id)
        if not product_account:
            raise ValidationError(
                _('Error !'),
                _('There is no expense account defined for this'
                    ' product: "%s") % (line.product_id.name'))
        if not journal_id:
            raise ValidationError(
                _('Error !',
                    'You have not defined Travel Expense Supplier Journal...'))
        invoice_line = (0, 0, {
            'name': _('%s (TMS Expense Record %s)') % (line.product_id.name,
                                                       line.expense_id.name),
            'origin': line.expense_id.name,
            'account_id': product_account,
            'quantity': line.product_qty,
            'price_unit': line.unit_price,
            'invoice_line_tax_ids':
            [(6, 0,
                [x.id for x in line.tax_ids])],
            'uom_id': line.product_uom_id.id,
            'product_id': line.product_id.id,
        })
        notes = line.expense_id.name + ' - ' + line.product_id.name
        partner_account = line.partner_id.property_account_payable_id.id
        invoice = {
            'origin': line.expense_id.name,
            'type': 'in_invoice',
            'journal_id': journal_id,
            'reference': line.invoice_number,
            'account_id': partner_account,
            'partner_id': line.partner_id.id,
            'invoice_line_ids': [invoice_line],
            'currency_id': line.expense_id.currency_id.id,
            'payment_term_id': (
                line.partner_id.property_supplier_payment_term_id.id
                if
                line.partner_id.property_supplier_payment_term_id
                else False),
            'fiscal_position_id': (
                line.partner_id.property_account_position_id.id or False),
            'comment': notes,
            'operating_unit_id': line.expense_id.operating_unit_id.id,
        }
        invoice_id = self.env['account.invoice'].create(invoice)
        line.write({'invoice_id': invoice_id.id})
        return invoice_id

    @api.multi
    def reconcile_supplier_invoices(self, invoice_ids, move_id):
        move_line_obj = self.env['account.move.line']
        for invoice in invoice_ids:
            move_ids = []
            invoice_str_id = str(invoice.id)
            expense_move_line = move_line_obj.search(
                [('move_id', '=', move_id.id), (
                    'name', 'ilike', invoice_str_id)])
            if not expense_move_line:
                raise ValidationError(
                    _('Error ! Move line was not found,'
                        ' please check your data.'))
            move_ids.append(expense_move_line.id)
            for move_line in invoice.move_id.line_ids:
                if move_line.account_id.internal_type == 'payable':
                    invoice_move_line_id = move_line
            move_ids.append(invoice_move_line_id.id)
            reconcile_ids = move_line_obj.browse(move_ids)
            reconcile_ids.reconcile()
        return True

    @api.onchange('operating_unit_id', 'unit_id')
    def _onchange_operating_unit_id(self):
        travels = self.env['tms.travel'].search([
            ('operating_unit_id', '=', self.operating_unit_id.id),
            ('state', '=', 'done'),
            ('unit_id', '=', self.unit_id.id)])
        self.employee_id = False
        return {
            'domain': {
                'employee_id': [
                    ('id', 'in', [x.employee_id.id for x in travels]),
                    ('driver', '=', True)
                ]
            }
        }

    @api.multi
    def get_amount_total(self):
        for rec in self:
            amount_subtotal = 0.0
            for line in rec.expense_line_ids:
                if line.line_type in ['real_expense', 'fuel', 'fuel_cash']:
                    amount_subtotal += line.price_subtotal
            return amount_subtotal

    @api.multi
    def get_amount_tax(self):
        for rec in self:
            tax_amount = 0.0
            for line in rec.expense_line_ids:
                if line.line_type in ['real_expense', 'fuel', 'fuel_cash']:
                    tax_amount += line.tax_amount
            return tax_amount

    @api.multi
    def get_value(self, type_line):
        for rec in self:
            value = 0.0
            for line in rec.expense_line_ids:
                if line.line_type == type_line:
                    value += line.price_total
        return value

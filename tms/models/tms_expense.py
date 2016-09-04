# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError


class TmsExpense(models.Model):
    _name = 'tms.expense'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Travel Expenses'
    _order = 'name desc'

    name = fields.Char(readonly=True)
    base_id = fields.Many2one('tms.base', string='Base', required=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Driver', required=True,
        domain=[('driver', '=', True)])
    travel_ids = fields.Many2many(
        'tms.travel',
        string='Travels')
    unit_id = fields.Many2one(
        'fleet.vehicle', 'Unit', required=True,
        domain=[('fleet_type', '=', 'tractor')])
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True, readonly=True,
        default=lambda self: self.env.user.company_id.currency_id.id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled')], 'Expense State', readonly=True,
        help="Gives the state of the Travel Expense. ",
        default='draft')
    date = fields.Date(
        'Date', required=True,
        default=fields.Date.today)
    expense_line_ids = fields.One2many(
        'tms.expense.line', 'expense_id', 'Expense Lines')
    amount_real_expense = fields.Float(
        compute='_amount_all',
        string='Expenses',
        store=True)
    amount_madeup_expense = fields.Float(
        compute='_compute_madeup',
        string='Fake Expenses',
        store=True)
    fuel_qty = fields.Float(
        compute='_amount_all',
        string='Fuel Qty',
        store=True)
    amount_fuel = fields.Float(
        compute='_amount_all',
        string='Fuel (Voucher)',
        store=True)
    amount_salary = fields.Float(
        compute='_amount_all',
        string='Salary',
        store=True)
    amount_net_salary = fields.Float(
        compute='_amount_all',
        string='Net Salary',
        store=True)
    amount_salary_retention = fields.Float(
        compute='_amount_all',
        string='Salary Retentions',
        store=True)
    amount_salary_discount = fields.Float(
        compute='_amount_all',
        string='Salary Discounts',
        store=True)
    amount_advance = fields.Float(
        compute='_amount_all',
        string='Advances',
        store=True)
    amount_balance = fields.Float(
        compute='_amount_all',
        string='Balance',
        store=True)
    amount_balance2 = fields.Float(
        compute='_amount_all',
        string='Balance',
        store=True)
    amount_tax_total = fields.Float(
        compute='_amount_all',
        string='Taxes (All)',
        store=True)
    amount_tax_real = fields.Float(
        compute='_amount_all',
        string='Taxes (Real)',
        store=True)
    amount_total_real = fields.Float(
        compute='_amount_all',
        string='Total (Real)',
        store=True)
    amount_total_total = fields.Float(
        compute='_amount_all',
        string='Total (All)',
        store=True)
    amount_subtotal_real = fields.Float(
        compute='_amount_all',
        string='SubTotal (Real)',
        store=True)
    amount_subtotal_total = fields.Float(
        string='SubTotal (All)',
        store=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    last_odometer = fields.Float('Last Read')
    vehicle_odometer = fields.Float('Vehicle Odometer')
    current_odometer = fields.Float('Current Read')
    distance_routes = fields.Float(
        compute='_amount_all',
        string='Distance from routes',
        help="Routes Distance")
    distance_real = fields.Float(
        compute='_amount_all',
        string='Distance Real',
        help="Route obtained by electronic reading and/or GPS")
    odometer_log_id = fields.Many2one(
        'fleet.vehicle.odometer', 'Odometer Record')
    global_fuel_efficiency_routes = fields.Float(
        # compute=_get_fuel_efficiency,
        string='Global Fuel Efficiency Routes')
    loaded_fuel_efficiency = fields.Float(
        'Loaded Fuel Efficiency')
    unloaded_fuel_efficiency = fields.Float(
        'Unloaded Fuel Efficiency')
    notes = fields.Text()
    move_id = fields.Many2one(
        'account.move', 'Journal Entry', readonly=True,
        help="Link to the automatically generated Journal Items.")
    paid = fields.Boolean(
        # compute=_paid
        )
    advance_ids = fields.One2many(
        'tms.advance', 'expense_id', string='Advances', readonly=True)
    fuel_qty_real = fields.Float(
        'Fuel Qty Real',
        help="Fuel Qty computed based on Distance Real and Global Fuel "
        "Efficiency Real obtained by electronic reading and/or GPS")
    fuel_diff = fields.Float(
        string="Fuel Difference",
        help="Fuel Qty Difference between Fuel Vouchers + Fuel Paid in Cash "
        "versus Fuel qty computed based on Distance Real and Global Fuel "
        "Efficiency Real obtained by electronic reading and/or GPS"
        # compute=_get_fuel_diff
        )
    global_fuel_efficiency_real = fields.Float(
        # compute=_get_fuel_diff,
        string='Global Fuel Efficiency Real')
    fuel_log_ids = fields.One2many(
        'fleet.vehicle.log.fuel', 'expense_id')

    @api.depends('travel_ids')
    def _amount_all(self):
        for rec in self:
            for travel in rec.travel_ids:
                rec.distance_real += travel.distance_driver
                rec.distance_routes += travel.distance_route
                for advance in travel.advance_ids:
                    if advance.auto_expense:
                        rec.amount_real_expense += advance.amount
                        rec.amount_total_real += advance.amount
                    else:
                        rec.amount_salary_discount += advance.amount
                rec.amount_fuel = 0.0
                driver_salary = 0.0
                for fuel_log in travel.fuel_log_ids:
                    rec.amount_fuel += fuel_log.price_total
                    rec.amount_tax_total += (
                        fuel_log.tax_amount +
                        fuel_log.special_tax_amount)
                if len(travel.waybill_ids.driver_factor_ids) > 0:
                    for waybill in travel.waybill_ids:
                        for waybill_factor in (
                                waybill.driver_factor_ids):
                            driver_salary = 0.0
                            driver_salary += (
                                waybill_factor.
                                get_amount(waybill.product_weight,
                                           waybill.distance_route,
                                           waybill.distance_real,
                                           waybill.product_qty,
                                           waybill.product_volume,
                                           waybill.amount_total))
                            rec.amount_salary += driver_salary
                else:
                    for factor in travel.driver_factor_ids:
                        driver_salary += factor.get_amount()
                rec.amount_subtotal_total = rec.amount_fuel
            rec.amount_total_total = (rec.amount_fuel +
                                      rec.amount_tax_total)
            rec.amount_total_real = (rec.amount_salary +
                                     rec.amount_fuel +
                                     rec.amount_total_real)
            rec.amount_balance = (rec.amount_total_real -
                                  rec.amount_advance)
            for discount in rec.expense_line_ids:
                if discount.line_type == 'madeup_expense':
                    rec.amount_madeup_expense = discount.price_total
                if discount.line_type == 'salary_discount':
                    rec.amount_salary_discount += discount.price_total
                    rec.amount_salary = (rec.amount_salary -
                                         discount.price_total)

    @api.multi
    def get_travel_info(self):
        for rec in self:
            rec.expense_line_ids.unlink()
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
            for travel in rec.travel_ids:
                travel.write({
                    'state': 'closed',
                    'expense_id': rec.id
                })
                for advance in travel.advance_ids:
                    if advance.state != 'confirmed':
                        raise ValidationError(_(
                            'Oops! All the advances must be confirmed'
                            '\n Name of advance not confirmed: ' +
                            advance.name +
                            '\n State: ' + advance.state))
                    else:
                        advance.write({
                            'state': 'closed',
                            'expense_id': rec.id
                        })
                        if advance.auto_expense:
                            rec.expense_line_ids.create({
                                'name': (str(advance.base_id.
                                             advance_product_id.name)),
                                'travel_id': travel.id,
                                'expense_id': rec.id,
                                'line_type': "real_expense",
                                'price_total': advance.amount,
                                'base_id': advance.base_id.id
                            })
                for fuel_log in travel.fuel_log_ids:
                    if fuel_log.state != 'confirmed':
                        raise ValidationError(_(
                            'Oops! All the voucher must be confirmed'
                            '\n Name of voucher not confirmed: ' +
                            fuel_log.name +
                            '\n State: ' + fuel_log.state))
                    else:
                        fuel_log.write({
                            'state': 'closed',
                            'expense_id': rec.id
                        })
                        rec.expense_line_ids.create({
                            'name': "Fuel voucher: " + str(fuel_log.name),
                            'travel_id': travel.id,
                            'expense_id': rec.id,
                            'line_type': 'fuel',
                            'price_total': fuel_log.price_total,
                            'is_invoice': fuel_log.invoice_paid,
                            'base_id': fuel_log.base_id.id
                            })
                rec.expense_line_ids.create({
                    'name': "salary per travel: " + str(travel.name),
                    'travel_id': travel.id,
                    'expense_id': rec.id,
                    'line_type': "salary",
                    'price_total': rec.amount_salary,
                    'base_id': travel.base_id.id
                })

    @api.model
    def create(self, values):
        expense = super(TmsExpense, self).create(values)
        sequence = expense.base_id.expense_sequence_id
        expense.name = sequence.next_by_id()
        return expense

    @api.multi
    def write(self, values):
        res = super(TmsExpense, self).write(values)
        for rec in self:
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
                            fields.Datetime.now())
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
                            fields.Datetime.now())
            rec.message_post(body=message)
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        for rec in self:
            for advance in rec.advance_ids:
                advance.state = 'closed'
            for fuel_log in rec.fuel_log_ids:
                fuel_log.state = 'closed'
            message = _('<b>Expense Confirmed.</b></br><ul>'
                        '<li><b>Confirmed by: </b>%s</li>'
                        '<li><b>Confirmed at: </b>%s</li>'
                        '</ul>') % (
                            self.env.user.name,
                            fields.Datetime.now())
            rec.message_post(body=message)
        self.state = 'confirmed'

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'

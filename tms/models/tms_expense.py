# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models


class TmsExpense(models.Model):
    _name = 'tms.expense'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Travel Expenses'
    _order = 'name desc'

    name = fields.Char(readonly=True)
    base_id = fields.Many2one('tms.base', string='Base', required=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Driver', required=True,
        domain=[('tms_category', '=', 'driver')])
    travel_ids = fields.Many2many(
        'tms.travel',
        string='Travels')
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
    expense_line = fields.One2many(
        'tms.expense.line', 'expense_id', 'Expense Lines')
    amount_real_expense = fields.Float(
        # compute=_amount_all,
        string='Expenses')
    amount_madeup_expense = fields.Float(
        # compute=_amount_all,
        string='Fake Expenses')
    fuel_qty = fields.Float(
        # compute=_amount_all,
        string='Fuel Qty')
    amount_fuel = fields.Float(
        # compute=_amount_all,
        string='Fuel (Cash)')
    amount_salary = fields.Float(
        # compute=_amount_all,
        string='Salary')
    amount_net_salary = fields.Float(
        # compute=_amount_all,
        string='Net Salary')
    amount_salary_retention = fields.Float(
        # compute=_amount_all,
        string='Salary Retentions')
    amount_salary_discount = fields.Float(
        # compute=_amount_all,
        string='Salary Discounts')
    amount_advance = fields.Float(
        # compute=_amount_all,
        string='Advances')
    amount_balance = fields.Float(
        # compute=_amount_all,
        string='Balance')
    amount_balance2 = fields.Float(
        # compute=_amount_all,
        string='Balance')
    amount_tax_total = fields.Float(
        # compute=_amount_all,
        string='Taxes (All)')
    amount_tax_real = fields.Float(
        # compute=_amount_all,
        string='Taxes (Real)')
    amount_total_real = fields.Float(
        # compute=_amount_all,
        string='Total (Real)')
    amount_total_total = fields.Float(
        # compute=_amount_all,
        string='Total (All)')
    amount_subtotal_real = fields.Float(
        # compute=_amount_all,
        string='SubTotal (Real)')
    amount_subtotal_total = fields.Float(
        # compute=_amount_all,
        string='SubTotal (All)')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    last_odometer = fields.Float('Last Read')
    vehicle_odometer = fields.Float('Vehicle Odometer')
    current_odometer = fields.Float('Current Read')
    distance_routes = fields.Float(
        # compute=_get_route_distance,
        string='Distance from routes',
        help="Routes Distance")
    distance_real = fields.Float(
        'Distance Real',
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

    @api.model
    def create(self, values):
        expense = super(TmsExpense, self).create(values)
        sequence = expense.base_id.expense_sequence_id
        expense.name = sequence.next_by_id()
        return expense

    @api.multi
    def action_draft(self):
        self.state = 'draft'
        self.amount_fuel = 0.0
        self.amount_subtotal_total = 0.0
        self.amount_tax_total = 0.0
        self.amount_total_total = 0.0
        self.amount_salary = 0.0
        self.amount_real_expense = 0.0
        self.amount_total_real = 0.0
        self.amount_advance = 0.0
        self.amount_balance = 0.0
        self.amount_salary_discount = 0.0

    @api.multi
    def action_confirm(self):
        for rec in self:
            rec.expense_line = {}
            rec.amount_real_expense = 0.0
            rec.amount_total_real = 0.0
            rec.amount_advance = 0.0
            rec.amount_balance = 0.0
            rec.amount_salary_discount = 0.0
            rec.salary_discount = 0.0
            for travel in rec.travel_ids:
                for advance in travel.advance_ids:
                    rec.advance_ids += advance
                    rec.amount_advance += advance.amount
                    if advance.auto_expense:
                        rec.amount_real_expense += advance.amount
                        rec.amount_total_real += advance.amount
                        rec.expense_line.create({
                            'name': (str(advance.base_id.
                                         advance_product_id.name)),
                            'travel_id': travel.id,
                            'expense_id': rec.id,
                            'line_type': "real_expense",
                            'price_total': advance.amount,
                            'base_id': advance.base_id.id,
                        })
                    else:
                        rec.amount_salary_discount += advance.amount
                rec.amount_fuel = 0.0
                driver_salary = 0.0
                for fuel_log in travel.fuel_log_ids:
                    rec.expense_line.create({
                        'name': "Fuel voucher: " + str(fuel_log.name),
                        'travel_id': travel.id,
                        'expense_id': rec.id,
                        'line_type': "fuel",
                        'price_total': fuel_log.price_total,
                        'is_invoice': fuel_log.invoice_paid,
                        'base_id': fuel_log.base_id.id
                        })
                    rec.fuel_log_ids += fuel_log
                    rec.amount_fuel += fuel_log.price_total
                    rec.amount_tax_total += (
                        fuel_log.tax_amount +
                        fuel_log.special_tax_amount)
                if len(travel.waybill_ids) > 0:
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
                                           waybill_factor.factor))
                            rec.amount_salary += driver_salary
                else:
                    for factor in travel.driver_factor_ids:
                        driver_salary += factor.get_amount()
                rec.amount_subtotal_total = rec.amount_fuel
            for discount in rec.expense_line:
                if discount.line_type == 'salary_discount':
                    rec.amount_salary_discount += discount.price_total
                    rec.amount_salary = (rec.amount_salary -
                                         discount.price_total)

            rec.amount_total_total = (rec.amount_fuel +
                                      rec.amount_tax_total)
            rec.amount_total_real = (rec.amount_salary +
                                     rec.amount_fuel +
                                     rec.amount_total_real)
            rec.amount_balance = (rec.amount_total_real -
                                  rec.amount_advance)
            self.state = 'confirmed'

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
    def action_cancel(self):
        self.state = 'cancel'

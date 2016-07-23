# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class TmsExpense(models.Model):
    _name = 'tms.expense'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Travel Expenses'
    _order = 'name desc'

    name = fields.Char(readonly=True)
    base_id = fields.Many2one('tms.base', string='Base', required=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Driver', required=True,
        domain=[('tms_category', '=', 'driver')],)
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
    amount_fuel_voucher = fields.Float(
        # compute=_amount_all,
        string='Fuel (Voucher)')
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

    @api.model
    def create(self, values):
        expense = super(TmsExpense, self).create(values)
        sequence = expense.base_id.expense_sequence_id
        expense.name = sequence.next_by_id()
        return expense

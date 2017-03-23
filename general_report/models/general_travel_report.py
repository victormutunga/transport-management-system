# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from datetime import datetime, timedelta


class ReportGeneralTravel(models.Model):
    _name = "report.general.travel"

    name = fields.Char(
        string='Date',
    )
    parent_id = fields.Many2one(
        'report.general.travel',
        string='Field Label',
    )
    child_ids = fields.One2many(
        'report.general.travel',
        'parent_id',
        string='Field Label',
    )
    travel_id = fields.Many2one(
        'tms.travel',
        string='Travel',
    )
    no_travel = fields.Integer(
        'Travels Done ',
        compute="get_no_travels"
    )
    distance_real = fields.Float(
        'Kilometers Traveled',
        compute="get_distance_real"
    )
    income = fields.Float(
        'Revenue Generated',
        default=0,
        compute="get_income"
    )
    expense_travel = fields.Float(
        'Travel expenses',
        compute="get_expense_travel"
    )
    expense_mtto = fields.Float(
        'Maintenance expenses',
        compute="get_expense_mtto"
    )
    utility = fields.Float(
        'Utilidad',
        compute="get_utility"
    )
    percentage_utility = fields.Float(
        'Percentage of Utility',
        compute="get_percentage_utility"
    )
    expense_fuel = fields.Float(
        'Fuel Expenses',
        compute="get_expense_fuel"
    )
    tires = fields.Float(
        'Tire Intake',
        compute="get_tires"
    )
    fuel = fields.Float(
        'Fuel Strips',
        compute="get_fuel"
    )
    efficienty_fuel = fields.Float(
        'Fuel Performance',
        compute="get_efficienty_fuel"
    )
    expense_km = fields.Float(
        'Cost Per Kilometer',
        compute="get_expense_km"
    )
    income_km = fields.Float(
        'Revenue per kilometer',
        compute="get_income_km"
    )
    utility_km = fields.Float(
        'Utility per kilometer',
        compute="get_utility_km"
    )

    @api.depends('travel_id')
    def get_no_travels(self):
        for rec in self:
            if not rec.child_ids:
                rec.no_travel = 1
        for rec in self:
            if rec.parent_id and rec.child_ids:
                rec.no_travel = len(rec.child_ids)
        for rec in self:
            if not rec.parent_id and rec.child_ids:
                rec.no_travel = sum([x.no_travel for x in rec.child_ids])

    @api.depends('travel_id')
    def get_distance_real(self):
        for rec in self:
            if not rec.child_ids:
                rec.distance_real = rec.travel_id.distance_route
        for rec in self:
            if rec.parent_id and rec.child_ids:
                rec.distance_real = sum(
                    [x.distance_real for x in rec.child_ids])
        for rec in self:
            if not rec.parent_id and rec.child_ids:
                rec.distance_real = sum(
                    [x.distance_real for x in rec.child_ids])

    @api.depends('travel_id')
    def get_income(self):
        for rec in self:
            if not rec.child_ids:
                rec.income = sum(
                    [x.amount_total for x in
                        rec.travel_id.waybill_ids if x.invoice_paid])
        for rec in self:
            if rec.parent_id and rec.child_ids:
                rec.income = sum(
                    [x.income for x in rec.child_ids])
        for rec in self:
            if not rec.parent_id and rec.child_ids:
                rec.income = sum(
                    [x.income for x in rec.child_ids])

    @api.depends('travel_id')
    def get_expense_travel(self):
        for rec in self:
            if not rec.child_ids:
                rec.expense_travel = sum(
                    [x.amount for x in
                        rec.travel_id.advance_ids if x.paid])
        for rec in self:
            if rec.parent_id and rec.child_ids:
                rec.expense_travel = sum(
                    [x.expense_travel for x in rec.child_ids])
        for rec in self:
            if not rec.parent_id and rec.child_ids:
                rec.expense_travel = sum(
                    [x.expense_travel for x in rec.child_ids])

    @api.depends('travel_id')
    def get_expense_mtto(self):
        for rec in self:
            rec.expense_mtto = 0.0

    @api.depends('travel_id')
    def get_utility(self):
        for rec in self:
            if not rec.child_ids:
                rec.utility = (
                    rec.income - (
                        rec.expense_travel + rec.expense_mtto +
                        rec.expense_fuel))
        for rec in self:
            if rec.parent_id and rec.child_ids:
                rec.utility = sum(
                    [x.utility for x in rec.child_ids])
        for rec in self:
            if not rec.parent_id and rec.child_ids:
                rec.utility = sum(
                    [x.utility for x in rec.child_ids])

    @api.depends('travel_id')
    def get_percentage_utility(self):
        for rec in self:
            if not rec.child_ids:
                if rec.income > 0:
                    rec.percentage_utility = (rec.utility * 100 / rec.income)
                else:
                    rec.percentage_utility = 0
        for rec in self:
            if rec.parent_id and rec.child_ids:
                rec.percentage_utility = sum(
                    [x.percentage_utility for x in rec.child_ids])
        for rec in self:
            if not rec.parent_id and rec.child_ids:
                rec.percentage_utility = sum(
                    [x.percentage_utility for x in rec.child_ids])

    @api.depends('travel_id')
    def get_expense_fuel(self):
        for rec in self:
            if not rec.child_ids:
                rec.expense_fuel = sum(
                    [x.price_total for x in
                        rec.travel_id.fuel_log_ids if x.state == 'closed'])
        for rec in self:
            if rec.parent_id and rec.child_ids:
                rec.expense_fuel = sum(
                    [x.expense_fuel for x in rec.child_ids])
        for rec in self:
            if not rec.parent_id and rec.child_ids:
                rec.expense_fuel = sum(
                    [x.expense_fuel for x in rec.child_ids])

    @api.depends('travel_id')
    def get_tires(self):
        for rec in self:
            rec.tires = 0.0

    @api.depends('travel_id')
    def get_fuel(self):
        for rec in self:
            if not rec.child_ids:
                rec.fuel = sum(
                    [x.product_qty for x in
                        rec.travel_id.fuel_log_ids if x.state == 'closed'])
        for rec in self:
            if rec.parent_id and rec.child_ids:
                rec.fuel = sum(
                    [x.fuel for x in rec.child_ids])
        for rec in self:
            if not rec.parent_id and rec.child_ids:
                rec.fuel = sum(
                    [x.fuel for x in rec.child_ids])

    @api.depends('travel_id')
    def get_efficienty_fuel(self):
        for rec in self:
            rec.efficienty_fuel = 0.0

    @api.depends('travel_id')
    def get_expense_km(self):
        for rec in self:
            rec.expense_km = 0.0

    @api.depends('travel_id')
    def get_income_km(self):
        for rec in self:
            rec.income_km = 0.0

    @api.depends('travel_id')
    def get_utility_km(self):
        for rec in self:
            rec.utility_km = 0.0

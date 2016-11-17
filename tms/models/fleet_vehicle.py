# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class OldFleetVehicle(models.Model):
    """
    This ugly code is needed to override fields.function from old api.
    See https://github.com/odoo/odoo/issues/3922
    """
    _name = 'fleet.vehicle'
    _inherit = 'fleet.vehicle'

    name = fields.Char('Name')


class FleetVehicle(models.Model):
    _name = 'fleet.vehicle'
    _inherit = 'fleet.vehicle'
    _description = "Vehicle"
    _order = 'name asc'

    base_id = fields.Many2one('operating.unit', string='Base')
    year_model = fields.Char(string='Year Model')
    serial_number = fields.Char(string='Serial Number')
    registration = fields.Char(string='Registration')
    fleet_type = fields.Selection(
        [('tractor', 'Motorized Unit'),
         ('trailer', 'Trailer'),
         ('dolly', 'Dolly'),
         ('other', 'Other')],
        string='Unit Fleet Type')
    notes = fields.Text()
    active = fields.Boolean(default=True)
    driver_id = fields.Many2one('hr.employee', string="Driver")
    expense_ids = fields.One2many('tms.expense', 'unit_id', string='Expenses')
    engine_id = fields.Many2one('fleet.vehicle.engine', string='Engine')

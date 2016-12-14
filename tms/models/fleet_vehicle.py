# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models
from openerp.osv import fields as old_fields


class OldFleetVehicle(models.Model):
    """ This ugly code is needed to override fields.function from old api.
    See https://github.com/odoo/odoo/issues/3922
    """
    _name = 'fleet.vehicle'
    _inherit = 'fleet.vehicle'
    _columns = {
        'name': old_fields.char('Name', required=True),
    }


class FleetVehicle(models.Model):
    _name = 'fleet.vehicle'
    _inherit = 'fleet.vehicle'
    _description = "Vehicle"
    _order = 'name asc'

    operating_unit_id = fields.Many2one(
        'operating.unit', string='Operating Unit')
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
    driver_id = fields.Many2one('res.partner', string="Driver")
    employee_id = fields.Many2one(
        'hr.employee',
        string="Driver",
        domain=[('driver', '=', True)])
    expense_ids = fields.One2many('tms.expense', 'unit_id', string='Expenses')
    engine_id = fields.Many2one('fleet.vehicle.engine', string='Engine')
    supplier_unit = fields.Boolean(string='Supplier Unit')
    unit_extradata_ids = fields.One2many(
        'tms.unit.extradata', 'unit_id', 'Extra Data')
    unit_expiry_ids = fields.One2many(
        'tms.unit.expiry', 'unit_id', 'Expiry Extra Data')

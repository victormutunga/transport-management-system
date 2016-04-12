# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argilsoft>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


# Units for Transportation
class FleetVehicle(models.Model):
    _name = 'fleet.vehicle'
    _inherit = 'fleet.vehicle'
    _description = "All motor/trailer units"

    name = fields.Char(string='Unit Name', size=64)
    year_model = fields.Char(string='Year Model', size=64)
    unit_type_id = fields.Many2one(
        'tms.unit.category', 'Unit Type',
        domain="[('type','=','unit_type')]")
    serial_number = fields.Char(string='Serial Number', size=64)
    registration = fields.Char(string='Registration', size=64)
    fleet_type = fields.Selection(
        [('tractor', 'Motorized Unit'),
         ('trailer', 'Trailer'),
         ('dolly', 'Dolly'),
         ('other', 'Other')],
        'Unit Fleet Type')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)

# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models


# from openerp.tools.translate import _

# Vehicle Odometer records


class FleetVehicleOdometer(models.Model):
    _inherit = ['fleet.vehicle.odometer']
    _name = 'fleet.vehicle.odometer'

    last_odometer = fields.Float(
        string='Last Read',
        required=True)
    current_odometer = fields.Float(
        string='Current Read',
        required=True)
    distance = fields.Float(
        string='Distance',
        required=True)
    travel_id = fields.Many2one('tms.travel', string='Travel')

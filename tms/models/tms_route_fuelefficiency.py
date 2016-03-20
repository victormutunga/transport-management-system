
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp import models, fields


# Route Fuel Efficiency by Motor
class TmsRouteFuelefficiency(models.Model):
    _name = "tms.route.fuelefficiency"
    _description = "Fuel Efficiency by Motor"

    tms_route_id = fields.Many2one('tms.route', 'Route', required=True)
    motor_id = fields.Many2one(
        'tms.unit.category', 'Motor', domain="[('type','=','motor')]",
        required=True)
    type = fields.Selection(
        [('tractor', 'Drive Unit'), ('one_trailer', 'Single Trailer'),
         ('two_trailer', 'Double Trailer')], 'Type', required=True)
    performance = fields.Float(
        'Performance', required=True, digits=(14, 4),
        help='Fuel Efficiency for this motor type')

    _sql_constraints = [
        ('route_motor_type_uniq', 'unique(tms_route_id, motor_id, type)',
            'Motor + Type must be unique !'),
    ]

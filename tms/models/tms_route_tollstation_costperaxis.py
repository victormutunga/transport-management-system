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


from openerp import fields, models

# Routes toll stations cost per axis


class TmsRouteTollstationCostperAxis(models.Model):
    _name = 'tms.route.tollstation.costperaxis'
    _description = 'Routes toll stations cost per axis'

    tms_route_tollstation_id = fields.Many2one(
        'tms.route.tollstation', 'Toll Station', required=True)
    unit_type_id = fields.Many2one(
        'tms.unit.category', 'Unit Type', domain="[('type','=','unit_type')]",
        required=True)
    axis = fields.Integer('Axis', required=True)
    cost_credit = fields.Float('Cost Credit', required=True, digits=(14, 4))
    cost_cash = fields.Float('Cost Cash', required=True, digits=(14, 4))

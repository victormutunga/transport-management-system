
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


# Routes toll stations
class TmsRouteTollstation(models.Model):
    _name = 'tms.route.tollstation'
    _description = 'Routes toll stations'

    company_id = fields.Many2one('res.company', 'Company', required=False)
    name = fields.Char('Name', size=64, required=True)
    place_id = fields.Many2one('tms.place', 'Place', required=True)
    partner_id = fields.Many2one('res.partner', 'Partner', required=True)
    credit = fields.Boolean('Credit')
    tms_route_ids = fields.Many2many(
        'tms.route', 'tms_route_tollstation_route_rel', 'route_id',
        'tollstation_id', 'Routes with this Toll Station')
    active = fields.Boolean('Active', default=True)
    tms_route_tollstation_costperaxis_ids = fields.One2many(
        'tms.route.tollstation.costperaxis', 'tms_route_tollstation_id',
        'Toll Cost per Axis', required=True)

    _defaults = {
        'active': True,
    }

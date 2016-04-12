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

from openerp import api, fields, models
from openerp.exceptions import UserError
from openerp.tools.translate import _

import requests

import simplejson as json


# Routes
class TmsRoute(models.Model):
    _name = 'tms.route'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Routes'

    name = fields.Char('Route Name', size=64, required=True, select=True)
    departure_id = fields.Many2one('tms.place', 'Departure', required=True)
    arrival_id = fields.Many2one('tms.place', 'Arrival', required=True)
    distance = fields.Float(
        'Distance (mi./kms)', digits=(14, 4),
        help='Route distance (mi./kms)')
    travel_time = fields.Float(
        'Travel Time (hrs)', digits=(14, 4),
        help='Route travel time (hours)')
    notes = fields.Text('Notes')
    active = fields.Boolean('Active', default=True)

    @api.multi
    def get_route_info(self):
        for rec in self:
            departure = {
                'latitude': rec.departure_id.latitude,
                'longitude': rec.departure_id.longitude
            }
            arrival = {
                'latitude': rec.arrival_id.latitude,
                'longitude': rec.arrival_id.longitude
            }
            if not departure['latitude'] and not departure['longitude']:
                raise UserError(_("The departure don't have coordinates."))
            if not arrival['latitude'] and not arrival['longitude']:
                raise UserError(_("The arrival don't have coordinates."))
            url = 'http://maps.googleapis.com/maps/api/distancematrix/json'
            origins = (str(departure['latitude']) + ',' +
                       str(departure['longitude']))
            destinations = (str(arrival['latitude']) + ',' +
                            str(arrival['longitude']))
            params = {
                'origins': origins,
                'destinations': destinations,
                'mode': 'driving',
                'language': self.env.lang,
                'sensor': 'false',
            }
            result = json.loads(requests.get(url, params=params).content)
            distance = duration = 0.0
            if result['status'] == 'OK':
                res = result['rows'][0]['elements'][0]
                distance = res['distance']['value'] / 1000.0
                duration = res['duration']['value'] / 3600.0
            self.distance = distance
            self.travel_time = duration

    @api.multi
    def open_in_google(self):
        for route in self:
            points = (
                str(route.departure_id.latitude) + ',' +
                str(route.departure_id.longitude) + ',' +
                str(route.arrival_id.latitude) + ',' +
                str(route.arrival_id.longitude))
            url = "/tms/static/src/googlemaps/get_route.html?" + points
        return {'type': 'ir.actions.act_url',
                'url': url,
                'nodestroy': True,
                'target': 'new'}

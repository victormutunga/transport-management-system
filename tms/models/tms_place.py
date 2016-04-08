# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import urllib as my_urllib
from openerp import fields, models, api
import simplejson as json


# Cities / Places
class TmsPlace(models.Model):
    _name = 'tms.place'
    _description = 'Cities / Places'

    name = fields.Char('Place', size=64, required=True, select=True)
    complete_name = fields.Char(compute='_compute_complete_name')
    state_id = fields.Many2one(
        'res.country.state',
        'State Name',
        required=True)
    country_id = fields.Many2one(
        'res.country',
        related='state_id.country_id',
        string='Country')
    latitude = fields.Float(
        'Latitude', required=False, digits=(20, 10),
        help='GPS Latitude')
    longitude = fields.Float(
        'Longitude', required=False, digits=(20, 10),
        help='GPS Longitude')

    @api.multi
    def get_coordinates(self):
        for rec in self:
            address = (rec.name + "," + rec.state_id.name + "," +
                       rec.country_id.name)
            google_url = (
                'http://maps.googleapis.com/maps/api/geocode/json?address=' +
                address.encode('utf-8') + '&sensor=false')
            result = json.load(my_urllib.urlopen(google_url))
            if result['status'] == 'OK':
                location = result['results'][0]['geometry']['location']
                self.latitude = location['lat']
                self.longitude = location['lng']

    @api.multi
    def open_in_google(self):
        for place in self:
            url = ("/tms/static/src/googlemaps/get_place_from_coords.html?" +
                   str(place.latitude) + ',' + str(place.longitude))
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'nodestroy': True,
            'target': 'new'}

    @api.depends('name', 'state_id')
    def _compute_complete_name(self):
        for record in self:
            record.complete_name = record.name + ', ' + record.state_id.name

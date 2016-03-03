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


from openerp.osv import osv, fields
import simplejson as json
import urllib as my_urllib


# Cities / Places
class tms_place(osv.osv):
    _name = 'tms.place'
    _description = 'Cities / Places'

    def _get_place_and_state(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):            
            xname = record.name + ', ' + record.state_id.code
            res[record.id] = xname
        return res

    _columns = {
        'company_id'    : fields.many2one('res.company', 'Company', required=False),
        'name'          : fields.char('Place', size=64, required=True, select=True),
        'complete_name' : fields.function(_get_place_and_state, method=True, type="char", size=100, string='Complete Name', store=True),
        'state_id'      : fields.many2one('res.country.state', 'State Name', required=True),
        'country_id'    : fields.related('state_id', 'country_id', type='many2one', relation='res.country', string='Country'),
        'latitude'      : fields.float('Latitude', required=False, digits=(20,10), help='GPS Latitude'),
        'longitude'     : fields.float('Longitude', required=False, digits=(20,10), help='GPS Longitude'),
        'route_ids'     : fields.many2many('tms.route', 'tms_route_places_rel', 'place_id', 'route_id', 'Routes with this Place'),        
    }

    _rec_name = 'complete_name'

    def  button_get_coords(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            address = rec.name + "," + rec.state_id.name + "," + rec.country_id.name
            google_url = 'http://maps.googleapis.com/maps/api/geocode/json?address=' + address.encode('utf-8') + '&sensor=false'
            result = json.load(my_urllib.urlopen(google_url))
            #print google_url
            #print result
            if result['status'] == 'OK':
                #print 'latitude: ', result['results'][0]['geometry']['location']['lat']
                #print 'longitude: ', result['results'][0]['geometry']['location']['lng']
                self.write(cr, uid, ids, {'latitude': result['results'][0]['geometry']['location']['lat'], 'longitude' : result['results'][0]['geometry']['location']['lng'] })
            #else:
                #print result['status']
        return True

    def button_open_google(self, cr, uid, ids, context=None):
        for place in self.browse(cr, uid, ids):
            url="/tms/static/src/googlemaps/get_place_from_coords.html?" + str(place.latitude) + ','+ str(place.longitude)
        return { 'type': 'ir.actions.act_url', 'url': url, 'nodestroy': True, 'target': 'new' }

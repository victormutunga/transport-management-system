
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

#
# Please note that these reports are not multi-currency !!!
#

from osv import fields, osv
import tools
from tools.translate import _


# Vista para ver la disponibilidad de unidades


class tms_travel_availability(osv.osv):
    _name = "tms.travel.availability"
    _description = "Unit availability for Travel"
    _auto = False
    _rec_name = 'name'
    _columns = {
        'name'                  : fields.many2one('fleet.vehicle', 'Unit', readonly=True),
        'supplier_unit'         : fields.boolean('Supplier Unit', readonly=True),
        'fleet_type'            : fields.selection([('tractor','Motorized Unit'), ('trailer','Trailer'), ('dolly','Dolly'), ('other','Other')], 'Unit Fleet Type', readonly=True),
        'shop_id'               : fields.many2one('sale.shop', 'Shop', readonly=True),
        'travel_id'             : fields.many2one('tms.travel', 'Travel', readonly=True),
        'trailer1_id'           : fields.many2one('fleet.vehicle', 'Trailer 1', readonly=True),
        'dolly_id'              : fields.many2one('fleet.vehicle', 'Dolly', readonly=True),
        'trailer2_id'           : fields.many2one('fleet.vehicle', 'Trailer 2', readonly=True),
        'employee_id'           : fields.many2one('hr.employee', 'Driver', readonly=True),

        'date'                  : fields.date('Travel Date', readonly=True),
        'date_start'            : fields.date('Date Start', readonly=True),
        'date_end'              : fields.date('Date End', readonly=True),

        'state'                 : fields.selection([                                   
                                    ('draft', 'Pending'),
                                    ('progress', 'Progress'),
                                    ('free', 'Free'),
                                    ], 'State',readonly=True),


        'framework'             : fields.char('Framework', size=64, readonly=True),
        'unit_type_id'          : fields.many2one('tms.unit.category', 'Unit Type', readonly=True),
        'route_id'              : fields.many2one('tms.route', 'Route', readonly=True),
        'departure'             : fields.many2one('tms.place', 'Departure', readonly=True),
        'arrival'               : fields.many2one('tms.place', 'Arrival', readonly=True),
        'waybill_id'            : fields.many2one('tms.waybill', 'Waybill', readonly=True),
        'waybill_date'          : fields.date('Waybill Date', readonly=True),
        'partner_id'            : fields.many2one('res.partner', 'Customer', readonly=True),
        'user_id'               : fields.many2one('res.users', 'Salesman', readonly=True),

    }

    _order = "name, date, shop_id"

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'tms_travel_availability')
        cr.execute ("""
CREATE OR REPLACE VIEW tms_travel_availability as
select row_number() over() as id,
a.id as name, a.supplier_unit, a.fleet_type,
b.shop_id, b.id travel_id, b.trailer1_id, b.dolly_id, b.trailer2_id, b.employee_id,
case when b.date is null then current_date else b.date end date, b.date_start, b.date_end, 
case  when b.state is null then 'free' else b.state end state,
b.framework,
a.unit_type_id, b.route_id, b.departure_id departure, b.arrival_id arrival,
c.id waybill_id,
c.date_order waybill_date,
c.partner_id,
b.user_id
from fleet_vehicle a
	left join tms_travel b on a.id = b.unit_id and b.state in ('draft','progress')
	left join tms_waybill c on c.travel_id = b.id and c.state <> 'cancelled'

order by  a.name, b.date, a.shop_id
;
        """)

tms_travel_availability()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

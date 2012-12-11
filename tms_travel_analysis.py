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

from osv import fields,osv
import tools

class tms_travel_analysis(osv.osv):
    _name = "tms.travel.analysis"
    _description = "Travel Analisys"
    _auto = False
    _rec_name = 'name'
    _columns = {
        'shop_id'               : fields.many2one('sale.shop', 'Shop', readonly=True),
        'name'                  : fields.char('Name', size=64, readonly=True),
        'date'                  : fields.date('Date', readonly=True),
        'year'                  : fields.integer('Year', readonly=True),
        'month'                 : fields.integer('Month', readonly=True),
        'day'                   : fields.integer('Day', readonly=True),
        'week'                  : fields.integer('Week of Year', readonly=True),
        'state'                 : fields.selection([
                                    ('draft', 'Pending'),
                                    ('progress', 'Progress'),
                                    ('done', 'Done'),
                                    ('closed', 'Closed'),
                                    ('cancel', 'Cancelled')
                                    ], 'State',readonly=True),
        'employee_id'           : fields.many2one('hr.employee', 'Driver', readonly=True),
        'framework'             : fields.char('Framework', size=64, readonly=True),
        'unit_type_id'          : fields.many2one('tms.unit.category', 'Unit Type', readonly=True),
        'unit_id'               : fields.many2one('tms.unit', 'Unit', readonly=True),
        'trailer1_id'           : fields.many2one('tms.unit', 'Trailer 1', readonly=True),
        'dolly_id'              : fields.many2one('tms.unit', 'Dolly', readonly=True),
        'trailer2_id'           : fields.many2one('tms.unit', 'Trailer 2', readonly=True),
        'route_id'              : fields.many2one('tms.route', 'Route', readonly=True),
        'departure'             : fields.many2one('tms.place', 'Departure', readonly=True),
        'arrival'               : fields.many2one('tms.place', 'Arrival', readonly=True),
        'waybill_id'            : fields.many2one('tms.waybill', 'Waybill', readonly=True),
        'waybill_date'          : fields.date('Date', readonly=True),
        'partner_id'            : fields.many2one('res.partner', 'Customer', readonly=True),
        'waybill_state'         : fields.selection([
                                    ('draft', 'Pending'),
                                    ('approved', 'Approved'),
                                    ('confirmed', 'Confirmed'),
                                    ('cancel', 'Cancelled')
                                    ], 'Waybill State',readonly=True),

        'waybill_sequence'      : fields.many2one('ir.sequence', 'Waybill Sequence', readonly=True),
        'currency_id'           : fields.many2one('res.currency', 'Currency', readonly=True),
        'waybill_type'          : fields.selection([
                                    ('self', 'Self'),
                                    ('outsourced', 'Outsourced'),
                                    ], 'Waybill Type', readonly=True),
        'invoice_id'            : fields.many2one('account.invoice', 'Invoice', readonly=True),
        'invoice_name'          : fields.char('Invoice Name',   size=64, readonly=True),
        'user_id'               : fields.many2one('res.users', 'Salesman', readonly=True),
        'product_id'            : fields.many2one('product.product', 'Line', readonly=True),
        'amount'                : fields.float('Amount', digits=(18,6), readonly=True),        
        'tms_category'          : fields.selection([
                                          ('freight','Freight'), 
                                          ('move','Move'), 
                                          ('insurance','Insurance'), 
                                          ('highway_tolls','Highway Tolls'), 
                                          ('other','Other'),
                                            ], "Income Category", readonly=True),

        'shipped_product_id'    : fields.many2one('product.product', 'Shipped Product', readonly=True),
        'qty'                   : fields.float('Product Qty', digits=(18,6), readonly=True),



    }

#    _order = "shop_id, date_order, name"

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'tms_travel_analysis')
        cr.execute ("""
CREATE OR REPLACE VIEW tms_travel_analysis as
select row_number() over() as id,
a.shop_id, a.name, a.date, 
EXTRACT(YEAR FROM a.date)::INTEGER as year,
EXTRACT(MONTH FROM a.date)::INTEGER as month,
EXTRACT(DAY FROM a.date)::INTEGER as day,
EXTRACT(WEEK FROM a.date)::INTEGER as week,
a.state, a.employee_id, a.framework, f.unit_type_id, 
a.unit_id, a.trailer1_id, a.dolly_id, a.trailer2_id, a.route_id, a.departure, a.arrival,
b.id as waybill_id, b.date_order as waybill_date, b.partner_id, b.state as waybill_state, b.sequence_id as waybill_sequence, b.currency_id, b.waybill_type, b.invoice_id, b.invoice_name, b.user_id,
c.product_id, c.price_subtotal / (select count(id) from tms_waybill_shipped_product where waybill_id=b.id)::FLOAT as amount,
d.tms_category, e.product_id as shipped_product_id, 
e.product_uom_qty / (select count(id) from tms_waybill_line where waybill_id=b.id)::FLOAT as qty
from tms_travel a 
	left join tms_waybill b on (a.id = b.travel_id and b.state in ('approved', 'confirmed'))	
	left join tms_waybill_line c on (c.waybill_id = b.id and c.line_type = 'product')
	left join product_product d on (c.product_id = d.id)
	left join tms_waybill_shipped_product e on (e.waybill_id = b.id)
	left join tms_unit f on (a.unit_id = f.id)
order by a.shop_id, a.name, a.date
;
        """)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

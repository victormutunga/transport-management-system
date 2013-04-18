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

class tms_waybill_analysis(osv.osv):
    _name = "tms.waybill.analysis"
    _description = "Waybill Analisys"
    _auto = False
    _rec_name = 'name'
    _columns = {
        'shop_id'               : fields.many2one('sale.shop', 'Shop', readonly=True),
        'waybill_category'      : fields.many2one('tms.waybill.category', 'Waybill Categ', readonly=True),
        'sequence_id'           : fields.many2one('ir.sequence', 'Sequence', readonly=True),
        'state'                 : fields.selection([
                                    ('draft', 'Pending'),
                                    ('approved', 'Approved'),
                                    ('confirmed', 'Confirmed'),
                                    ('cancel', 'Cancelled')
                                    ], 'State',readonly=True),
        'name'                  : fields.char('Name', size=64, readonly=True),
        'date_order'            : fields.date('Date', readonly=True),
        
        'year'                  : fields.integer('Year', readonly=True),
        'month'                 : fields.integer('Month', readonly=True),
        'day'                   : fields.integer('Day', readonly=True),
        'week'                  : fields.integer('Week of Year', readonly=True),
        'partner_id'            : fields.many2one('res.partner', 'Customer', readonly=True),
        'travel_id'             : fields.many2one('tms.travel', 'Travel', readonly=True),
        'employee_id'           : fields.many2one('hr.employee', 'Driver', readonly=True),
        'unit_id'               : fields.many2one('fleet.vehicle', 'Unit', readonly=True),
        'trailer1_id'           : fields.many2one('fleet.vehicle', 'Trailer 1', readonly=True),
        'dolly_id'              : fields.many2one('fleet.vehicle', 'Dolly', readonly=True),
        'trailer2_id'           : fields.many2one('fleet.vehicle', 'Trailer 2', readonly=True),
        'route_id'              : fields.many2one('tms.route', 'Route', readonly=True),
        'departure_id'          : fields.many2one('tms.place', 'Departure', readonly=True),
        'arrival_id'            : fields.many2one('tms.place', 'Arrival', readonly=True),
        'currency_id'           : fields.many2one('res.currency', 'Currency', readonly=True),
        'waybill_type'          : fields.selection([
                                    ('Self', 'Self'),
                                    ('outsourced', 'Outsourced'),
                                    ], 'Waybill Type', readonly=True),
        'invoice_id'            : fields.many2one('account.invoice', 'Invoice', readonly=True),
        'invoice_name'          : fields.char('Invoice Name',   size=64, readonly=True),
        'user_id'               : fields.many2one('res.users', 'Salesman', readonly=True),
        'tms_category'          : fields.selection([
                                          ('freight','Freight'), 
                                          ('move','Move'), 
                                          ('insurance','Insurance'), 
                                          ('highway_tolls','Highway Tolls'), 
                                          ('other','Other'),
                                            ], "Income Category", readonly=True),

        'product_id'            : fields.many2one('product.product', 'Line', readonly=True),
        'framework'             : fields.char('Framework', size=64, readonly=True),
        'shipped_product_id'    : fields.many2one('product.product', 'Shipped Product', readonly=True),
        'qty'                   : fields.float('Product Qty', digits=(18,6), readonly=True),
        'amount'                : fields.float('Amount', digits=(18,6), readonly=True),

    }

#    _order = "shop_id, date_order, name"

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'tms_waybill_analysis')
        cr.execute("""

create or replace view tms_waybill_analysis as
select row_number() over() as id,
a.shop_id, a.waybill_category, a.sequence_id,
a.state, a.name, a.date_order, 
EXTRACT(YEAR FROM a.date_order)::INTEGER as year,
EXTRACT(MONTH FROM a.date_order)::INTEGER as month,
EXTRACT(DAY FROM a.date_order)::INTEGER as day,
EXTRACT(WEEK FROM a.date_order)::INTEGER as week,
a.partner_id, a.travel_id, d.employee_id, d.unit_id, d.trailer1_id, d.dolly_id, d.trailer2_id,
d.route_id, e.departure_id, e.arrival_id,
a.currency_id, a.waybill_type, a.invoice_id, a.invoice_name, a.user_id, c.tms_category, b.product_id, 
d.framework, 
f.product_id as shipped_product_id,
sum(f.product_uom_qty) / (select count(id) from tms_waybill_line where waybill_id=a.id)::FLOAT
qty,
sum(b.price_subtotal) / (select count(id) from tms_waybill_shipped_product where waybill_id=a.id)::FLOAT
 amount

from tms_waybill a
	left join tms_waybill_line b on (b.waybill_id = a.id and b.line_type = 'product')
	left join product_product c on (c.id = b.product_id)
	left join tms_travel d on (a.travel_id = d.id)
	left join tms_route e on (d.route_id = e.id)
	left join tms_waybill_shipped_product f on (f.waybill_id = a.id)
group by a.id, c.id, a.shop_id, a.sequence_id,
a.state, a.name, a.date_order, 
a.partner_id, a.travel_id, d.employee_id, d.unit_id, d.trailer1_id, d.dolly_id, d.trailer2_id,
d.route_id, e.departure_id, e.arrival_id,
a.currency_id, a.waybill_type, a.invoice_id, a.invoice_name, a.user_id, c.tms_category, b.product_id, 
d.framework, b.price_subtotal, f.product_id
order by a.shop_id, a.date_order, a.name

;
        """)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

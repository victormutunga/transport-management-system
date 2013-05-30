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

class tms_expense_analysis(osv.osv):
    _name = "tms.expense.analysis"
    _description = "Travel Expenses Analisys"
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
                ('draft', 'Draft'),
                ('approved', 'Approved'),
                ('confirmed', 'Confirmed'),
                ('cancel', 'Cancelled')
                ], 'State',readonly=True),
        'employee_id'           : fields.many2one('hr.employee', 'Driver', readonly=True),
        'unit_id'               : fields.many2one('fleet.vehicle', 'Unit', readonly=True),
        'currency_id'           : fields.many2one('res.currency', 'Currency', readonly=True),
        'product_id'            : fields.many2one('product.product', 'Line', readonly=True),
        'expense_line_description' : fields.char('Description',   size=256, readonly=True),

        'travel_id'             : fields.many2one('tms.travel', 'Travel', readonly=True),
        'route_id'              : fields.many2one('tms.route', 'Route', readonly=True),
        'waybill_income'        : fields.float('Waybill Amount', digits=(18,6), readonly=True),        

        'travels'               : fields.integer('Travels', readonly=True),        
        'qty'                   : fields.float('Qty', digits=(18,6), readonly=True),        
        'price_unit'            : fields.float('Price Unit', digits=(18,6), readonly=True),        
        'subtotal'              : fields.float('SubTotal', digits=(18,6), readonly=True),        

    }

#    _order = "shop_id, date_order, name"

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'tms_travel_analysis')
        cr.execute ("""
CREATE OR REPLACE VIEW tms_expense_analysis as
select row_number() over() as id,
a.shop_id, a.name, a.date, 
EXTRACT(YEAR FROM a.date)::INTEGER as year,
EXTRACT(MONTH FROM a.date)::INTEGER as month,
EXTRACT(DAY FROM a.date)::INTEGER as day,
EXTRACT(WEEK FROM a.date)::INTEGER as week,
a.state, a.employee_id, a.unit_id, a.currency_id, 
b.product_id, b.name expense_line_description,
c.id travel_id, c.route_id, 
c.waybill_income/ (select count(id) from tms_expense_line x where x.expense_id = a.id) waybill_income,
(select count(name) from tms_travel where a.id=tms_travel.expense_id) travels,
b.product_uom_qty / (select count(name) from tms_travel where a.id=tms_travel.expense_id) qty,
b.price_unit / (select count(name) from tms_travel where a.id=tms_travel.expense_id) price_unit,
b.price_subtotal / (select count(name) from tms_travel where a.id=tms_travel.expense_id) subtotal
from tms_expense a
	inner join tms_expense_line b on a.id = b.expense_id 
	inner join tms_travel c on a.id = c.expense_id
	where a.state <> 'cancel'

order by a.shop_id, a.name, a.date
;
        """)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

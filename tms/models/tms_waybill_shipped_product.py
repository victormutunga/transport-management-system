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
import time
from datetime import datetime, date
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from pytz import timezone


# Class for Waybill Shipped Products
class tms_waybill_shipped_product(osv.osv):
    _name = 'tms.waybill.shipped_product'
    _description = 'Waybill Shipped Product'


    _columns = {
#        'agreement_id': fields.many2one('tms.agreement', 'Agreement', required=False, ondelete='cascade', select=True, readonly=True),
        'waybill_id': fields.many2one('tms.waybill', 'waybill', required=False, ondelete='cascade', select=True, readonly=True),
        'name': fields.char('Description', size=256, required=True, select=True),
        'product_id': fields.many2one('product.product', 'Product', 
                            domain=[
                                    ('tms_category', '=','transportable'), 
                                    ('tms_category', '=','move'), 
                                    ('tms_category', '=','insurance'), 
                                    ('tms_category', '=','highway_tolls'), 
                                    ('tms_category', '=','other'),
                                    ], change_default=True, required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True),
        'product_uom_qty': fields.float('Quantity (UoM)', digits=(16, 4), required=True),
        'notes': fields.text('Notes'),
        'waybill_partner_id': fields.related('waybill_id', 'partner_id', type='many2one', relation='res.partner', store=True, string='Customer'),
        'salesman_id':fields.related('waybill_id', 'user_id', type='many2one', relation='res.users', store=True, string='Salesman'),
        'shop_id': fields.related('waybill_id', 'shop_id', type='many2one', relation='sale.shop', string='Shop', store=True, readonly=True),
        'company_id': fields.related('waybill_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of sales order lines."),
    }
    _order = 'sequence, id desc'
    _defaults = {
        'product_uom_qty': 1,
        'sequence': 10,
    }

    def on_change_product_id(self, cr, uid, ids, product_id):
        res = {}
        if not product_id:
            return {}
        prod_obj = self.pool.get('product.product')
        for product in prod_obj.browse(cr, uid, [product_id], context=None):            
            res = {'value': {'product_uom' : product.uom_id.id,
                             'name': product.name}
                }
        return res



tms_waybill_shipped_product()
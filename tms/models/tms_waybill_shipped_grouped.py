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

# Grouped Shipped Quantity by Product


class TmsWaybillShippedGrouped(osv.osv):
    _name = "tms.waybill.shipped_grouped"
    _description = "Waybill Grouped Shipped Qty by Product"

    _columns = {
        'invoice_id':
        fields.many2one('account.invoice', 'Invoice',
                        required=True, ondelete='cascade'),
        'product_id':
        fields.many2one('product.product', 'Product', required=True),
        'quantity':
        fields.float('Quantity', digits=(16, 2), required=True),
        'product_uom':
        fields.many2one('product.uom', 'Unit of Measure ', required=True),
    }

    _defaults = {
        'quantity': 0,
    }

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

from openerp import models, fields

# Class for Waybill Shipped Products


class TmsWaybillShippedProduct(models.Model):
    _name = 'tms.waybill.shipped_product'
    _description = 'Waybill Shipped Product'

#  agreement_id': fields.many2one('tms.agreement', 'Agreement', required=False,
#       ondelete='cascade', select=True, readonly=True),
    waybill_id = fields.Many2one(
        'tms.waybill', 'waybill', required=False, ondelete='cascade',
        select=True, readonly=True)
    name = fields.Char('Description', size=256, required=True, select=True)
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[
            ('tms_category', '=', 'transportable'),
            ('tms_category', '=', 'move'),
            ('tms_category', '=', 'insurance'),
            ('tms_category', '=', 'highway_tolls'),
            ('tms_category', '=', 'other')],
        change_default=True, required=True)
    product_uom = fields.Many2one(
        'product.uom', 'Unit of Measure ', required=True)
    product_uom_qty = fields.Float(
        'Quantity (UoM)', digits=(16, 4), required=True,
        default=1)
    notes = fields.Text('Notes')
    waybill_partner_id = fields.Many2one(
        'waybill_id', 'partner_id', relation='res.partner', store=True,
        string='Customer')
    salesman_id = fields.Many2one(
        'waybill_id', 'user_id', relation='res.users', store=True,
        string='Salesman')
    shop_id = fields.Many2one(
        'waybill_id', 'shop_id', relation='sale.shop', string='Shop',
        store=True, readonly=True)
    company_id = fields.Many2one(
        'waybill_id', 'company_id', relation='res.company', string='Company',
        store=True, readonly=True)
    sequence = fields.Integer(
        'Sequence', help="Gives the sequence order when displaying a list of \
        sales order lines.", default=10)

    _order = 'sequence, id desc'

    def on_change_product_id(self, product_id):
        res = {}
        if not product_id:
            return {}
        prod_obj = self.pool.get('product.product')
        for product in prod_obj.browse([product_id], context=None):
            res = {'value': {'product_uom': product.uom_id.id,
                             'name': product.name}}
        return res

TmsWaybillShippedProduct()

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


class TmsWaybillShippedProduct(models.Model):
    _name = 'tms.shipped.product'
    _description = 'Shipped Product'

    waybill_id = fields.Many2one(
        'tms.waybill', string='waybill', ondelete='cascade',
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

    _order = 'sequence, id desc'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.name = self.product_id.name
        self.product_uom = self.product_id.uom_id

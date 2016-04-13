# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

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
        'res.partner',
        related='waybill_id.partner_id',
        store=True,
        string='Customer')
    salesman_id = fields.Many2one(
        'res.users',
        related='waybill_id.user_id',
        store=True,
        string='Salesman')
    # shop_id = fields.Many2one(
    #     'sale.shop',
    #     related='waybill_id.shop_id.id',
    #     string='Shop',
    #     store=True, readonly=True)
    # company_id = fields.Many2one(
    #     'res.company',
    #     related='waybill_id.company_id.id',
    #     string='Company',
    #     store=True, readonly=True)
    sequence = fields.Integer(
        'Sequence', help="Gives the sequence order when displaying a list of \
        sales order lines.", default=10)

    _order = 'sequence, id desc'

    def on_change_product_id(self, product_id):
        # res = {}
        # if not product_id:
        #     return {}
        # prod_obj = self.pool.get('product.product')
        # for product in prod_obj.browse([product_id], context=None):
        #     res = {'value': {'product_uom': product.uom_id.id,
        #                      'name': product.name}}
        return 'comida'

TmsWaybillShippedProduct()

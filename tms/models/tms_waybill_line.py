# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class TmsWaybillLine(models.Model):
    _name = 'tms.waybill.line'
    _description = 'Waybill Line'
    _order = 'sequence, id desc'

    waybill_id = fields.Many2one(
        'tms.waybill',
        string='Waybill',
        readonly=True)
    line_type = fields.Selection([
        ('product', 'Product'),
        ('note', 'Note')],
        'Line Type',
        required=True,
        default='product')
    name = fields.Char('Description', required=True)
    sequence = fields.Integer(
        help="Gives the sequence order when displaying a list of "
        "sales order lines.",
        default=10)
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        domain=[('sale_ok', '=', True)])
    price_unit = fields.Float(
        'Unit Price',
        required=True)
    price_subtotal = fields.Float(
        # compute=_amount_line,
        string='Subtotal')
    price_amount = fields.Float(
        # compute=_amount_line
        )
    price_discount = fields.Float(
        # compute=_amount_line,
        string='Discount'
        )
    price_total = fields.Float(
        string='Total Amount'
        )
    tax_amount = fields.Float()
    tax_id = fields.Many2many('account.tax', string='Taxes')
    product_uom_qty = fields.Float(
        string='Quantity (UoM)',
        default=1)
    product_uom = fields.Many2one(
        'product.uom',
        string='Unit of Measure ')
    discount = fields.Float(
        string='Discount (%)',
        help="Please use 99.99 format...")
    notes = fields.Text()
    waybill_partner_id = fields.Many2one(
        'res.partner',
        string='Customer')
    control = fields.Boolean()

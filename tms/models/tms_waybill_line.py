# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models


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

    @api.depends('price_unit', 'product_uom_qty')
    @api.multi
    def _amount_line(self):
        tax_obj = self.env['account.tax']
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(
                line.tax_id, price, line.product_uom_qty,
                line.product_id, line.waybill_id.partner_id)
            currency = line.waybill_id.currency_id
            line.price_total = self.currency_id.round(
                currency, taxes['total_included'])
            line.tax_amount = self.currency_id.round(
                currency, taxes['total_included']) - self.currency_id.round(
                currency, taxes['total'])
            line.price_subtotal = line.price_unit * line.product_uom_qty
            line.price_discount = line.price_subtotal * (
                (line.discount or 0.0) / 100.0)

    @api.onchange('product_uom_qty', 'price_unit',
                  'discount', 'product_id', 'partner_id')
    def on_change_amount(self):
        tax_factor = 0.00
        if tax_factor == 0.00:
            raise Warning(
                _('No taxes defined in product !'),
                _('You have to add taxes for this product. Para Mexico: '
                  'Tiene que agregar el IVA que corresponda y el IEPS con '
                  'factor 0.0.'))

        self.price_amount = self.price_unit * self.product_uom_qty
        self.price_discount = (
            (self.price_unit * self.product_uom_qty) * (self.discount / 100.0))
        self.price_subtotal = self.price_amount - self.price_discount
        self.tax_amount = (
            (self.price_amount - self.price_discount) * tax_factor)
        self.price_total = (
            (self.price_amount - self.price_discount) * (1.0 + tax_factor))

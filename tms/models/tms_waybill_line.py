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

from openerp import fields, models
import openerp.addons.decimal_precision as dp

# Class for Waybill Lines


class TmsWaybillLine(models.Model):
    _name = 'tms.waybill.line'
    _description = 'Waybill Line'

    def _amount_line(self, field_name, args):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        for line in self.browse(self):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(
                line.tax_id, price, line.product_uom_qty,
                line.product_id, line.waybill_id.partner_id)
            cur = line.waybill_id.currency_id
            amount_with_taxes = cur_obj.round(cur, taxes['total_included'])
            amount_tax = cur_obj.round(
                cur, taxes['total_included']) - cur_obj.round(
                cur, taxes['total'])
            price_subtotal = line.price_unit * line.product_uom_qty
            price_discount = price_subtotal * (line.discount or 0.0) / 100.0
            res[line.id] = {
                'price_total': amount_with_taxes,
                'price_amount': price_subtotal,
                'price_discount': price_discount,
                'price_subtotal': (price_subtotal - price_discount),
                'tax_amount': amount_tax,
            }
        return res

#   agreement_id = fields.Many2one(
#       'tms.agreement', 'Agreement', required=False, ondelete='cascade',
#       select=True, readonly=True)
    waybill_id = fields.Many2one(
        'tms.waybill', 'Waybill', required=False, ondelete='cascade',
        select=True, readonly=True)
    line_type = fields.Selection([
        ('product', 'Product'),
        ('note', 'Note'), ], 'Line Type', require=True, default='product')
    name = fields.Char('Description', size=256, required=True)
    sequence = fields.Integer(
        'Sequence',
        help="Gives the sequence order when displaying a list of sales \
        order lines.", default=10)
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('sale_ok', '=', True),
                ('tms_category', 'in',
                 ('freight', 'move', 'insurance', 'highway_tolls', 'other'))],
        change_default=True, ondelete='restrict')
    price_unit = fields.Float(
        'Unit Price', required=True,
        digits_compute=dp.get_precision('Sale Price'), default=0.0)
    price_subtotal = fields.Float(
        compute=_amount_line, method=True, string='Subtotal',
        digits_compute=dp.get_precision('Sale Price'), store=True,
        multi='price_subtotal')
    price_amount = fields.Float(
        compute=_amount_line, method=True, string='Price Amount',
        digits_compute=dp.get_precision('Sale Price'), store=True,
        multi='price_subtotal')
    price_discount = fields.Float(
        compute=_amount_line, method=True, string='Discount',
        digits_compute=dp.get_precision('Sale Price'), store=True,
        multi='price_subtotal')
    price_total = fields.Float(
        compute=_amount_line, method=True, string='Total Amount',
        digits_compute=dp.get_precision('Sale Price'), store=True,
        multi='price_subtotal')
    tax_amount = fields.Float(
        compute=_amount_line, method=True, string='Tax Amount',
        digits_compute=dp.get_precision('Sale Price'), store=True,
        multi='price_subtotal')
    tax_id = fields.Many2many(
        'account.tax', 'waybill_tax', 'waybill_line_id', 'tax_id', 'Taxes')
    product_uom_qty = fields.Float(
        'Quantity (UoM)', digits=(16, 4), default=1)
    product_uom = fields.Many2one('product.uom', 'Unit of Measure ')
    discount = fields.Float(
        'Discount (%)', digits=(16, 2), help="Please use 99.99 format...",
        default=0.0)
    notes = fields.text('Notes')
    waybill_partner_id = fields.Many2one(
        'waybill_id', 'partner_id', relation='res.partner', store=True,
        string='Customer')
    salesman_id = fields.Many2one(
        'waybill_id', 'user_id', relation='res.users', store=True,
        string='Salesman')
    company_id = fields.Many2one(
        'waybill_id', 'company_id', relation='res.company', string='Company',
        store=True, readonly=True)
    control = fields.Boolean('Control')

    _order = 'sequence, id desc'

    def on_change_product_id(self, product_id, partner_id):
        res = {}
        if not product_id:
            return {}
        lang = self.pool.get('lang', False)
        if not partner_id:
            raise Warning(
                ('No Customer Defined !'),
                ('Before choosing a product,\n select a customer in\
                    the form.'))
        partner_obj = self.pool.get('res.partner')
        if partner_id:
            lang = partner_obj.browse(partner_id).lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        fpos = partner_obj.browse(
            partner_id).property_account_position.id or False

        prod_obj = self.pool.get('product.product')
        fpos_obj = self.pool.get('account.fiscal.position')
        fpos = fpos and fpos_obj.browse(self) or False
        product_obj = prod_obj.browse(
            product_id, context=context_partner)
        taxes = product_obj.taxes_id
        res = {'value': {
            'product_uom': product_obj.uom_id.id,
            'name': product_obj.name,
            'tax_id': fpos_obj.map_tax(fpos, taxes),
        }}
        return res

    def on_change_amount(
            self, product_uom_qty, price_unit, discount,
            product_id, partner_id):
        res = {'value': {
            'price_amount': 0.0,
            'price_subtotal': 0.0,
            'price_discount': 0.0,
            'price_total': 0.0,
            'tax_amount': 0.0,
        }}
        if not (product_uom_qty and price_unit and product_id):
            return res
        fpos = self.pool.get('res.partner').browse(
            [partner_id])[0].property_account_position.id or False
        fpos_obj = self.pool.get('account.fiscal.position')
        tax_obj = self.pool.get('account.tax')
        fpos = fpos and fpos_obj.browse(self) or False
        prod_obj = self.pool.get('product.product')
        tax_factor = 0.00
        for line in tax_obj.browse(fpos_obj.map_tax(
                fpos, prod_obj.browse([product_id])[0].taxes_id)):
            # print line
            tax_factor = ((tax_factor + line.amount)
                          if line.amount != 0.0 else tax_factor)
#        if tax_factor == 0.00:
#            raise osv.except_osv(_('No taxes defined in product !'),
#         _('You have to add taxes for this product. Para Mexico: Tiene que
#           agregar el IVA que corresponda y el IEPS con factor 0.0.'))

        price_amount = price_unit * product_uom_qty
        price_discount = (price_unit * product_uom_qty) * (discount / 100.0)
        res = {'value': {
            'price_amount': price_amount,
            'price_discount': price_discount,
            'price_subtotal': (price_amount - price_discount),
            'tax_amount': (price_amount - price_discount) * tax_factor,
            'price_total':
            (price_amount - price_discount) * (1.0 + tax_factor),
        }}
        return res

TmsWaybillLine()

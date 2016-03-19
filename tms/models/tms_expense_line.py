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
import openerp.addons.decimal_precision as dp

# Class for Expense Lines


class TmsExpenseLine(models.Model):
    _name = 'tms.expense.line'
    _description = 'Expense Line'

    def _amount_line(self, field_name, args):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if self is None:
            context = {}
        for line in self.browse(context=context):
            price = line.price_unit
            partner_id = self.pool.get(
                'res.users').browse(self).company_id.partner_id.id
            addr_id = self.pool.get('res.partner').address_get(
                [partner_id], ['invoice'])['invoice']
            taxes = tax_obj.compute_all(
                line.product_id.supplier_taxes_id,
                price, line.product_uom_qty, addr_id,
                line.product_id, line.company_id.partner_id)
            cur = line.expense_id.currency_id
            amount_with_taxes = cur_obj.round(cur, taxes['total_included'])
            amount_tax = cur_obj.round(
                cur, taxes['total_included']) - (cur_obj.round(
                    cur, taxes['total']) or 0.0) + cur_obj.round(
                cur, line.special_tax_amount)
            price_subtotal = line.price_unit * line.product_uom_qty
            res[line.id] = {
                'price_subtotal': price_subtotal,
                'price_total': amount_with_taxes,
                'tax_amount': amount_tax,
            }
        return res

    operation_id = fields.Many2one(
        'tms.operation', 'Operation', ondelete='restrict',
        required=False, readonly=False)
    travel_id = fields.Many2one(
        'tms.travel', 'Travel', required=False)
    expense_id = fields.Many2one(
        'tms.expense', 'Expense', required=False, ondelete='cascade',
        select=True, readonly=True)
    line_type = fields.Selection(
        [
            ('real_expense', 'Real Expense'),
            ('madeup_expense', 'Made-up Expense'),
            ('salary', 'Salary'),
            ('salary_retention', 'Salary Retention'),
            ('salary_discount', 'Salary Discount'),
            ('fuel', 'Fuel'),
            ('indirect', 'Indirect'),
            ('negative_balance', 'Negative Balance'), ],
        'Line Type', require=True, default='real_expense')
    name = fields.Char('Description', size=256, required=True)
    sequence = fields.Integer(
        'Sequence',
        help="Gives the sequence order when displaying a list of \
        sales order lines.", order=1, default=10)
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('tms_category', 'in',
                ('expense_real', 'madeup_expense', 'salary',
                    'salary_retention', 'salary_discount'))],
        ondelete='restrict')
    price_unit = fields.Float(
        'Price Unit', required=True, digits=(16, 4), default=0.0)
    price_unit_control = fields.Float(
        'Price Unit', digits_compute=dp.get_precision('Sale Price'))
    price_subtotal = fields.Float(
        compute=_amount_line, method=True, string='SubTotal',
        digits_compute=dp.get_precision('Sale Price'), store=True,
        multi='price_subtotal')
    price_total = fields.Float(
        compute=_amount_line, method=True, string='Total',
        digits_compute=dp.get_precision('Sale Price'), store=True,
        multi='price_subtotal')
    tax_amount = fields.Float(
        compute=_amount_line, method=True, string='Tax Amount',
        digits_compute=dp.get_precision('Sale Price'), store=True,
        multi='price_subtotal')
    special_tax_amount = fields.Float(
        'Special Tax', required=False,
        digits_compute=dp.get_precision('Sale Price'), default=0.0)
    tax_id = fields.Many2many(
        'account.tax', 'expense_tax', 'tms_expense_line_id', 'tax_id', 'Taxes')
    product_uom_qty = fields.Float('Quantity (UoM)', digits=(16, 4), default=1)
    product_uom = fields.Many2one('product.uom', 'Unit of Measure ')
    notes = fields.Text('Notes')
    employee_id = fields.Many2one(
        compute='expense_id.employee_id', relation='hr.employee',
        store=True, string='Driver')
    shop_id = fields.Many2one('sale.shop', string='Shop')
    company_id = fields.Many2one(
        compute='expense_id.company_id', type='many2one',
        relation='res.company', string='Company', store=True, readonly=True)
    date = fields.Date(
        'expense_id', 'date', string='Date', store=True, readonly=True)
    state = fields.Char(
        'expense_id', 'state', string='State', size=64, store=True,
        readonly=True)
    fuel_voucher = fields.Boolean('Fuel Voucher'),
    control = fields.Boolean('Control')
    # Useful to mark those lines that must not be deleted for Expense Record
    # (like Fuel from Fuel Voucher, Toll Stations payed without cash
    # (credit card, voucher, etc)
    automatic = fields.Boolean(
        'Automatic', help="Check this if you want to create Advances and/or \
        Fuel Vouchers for this line automatically"),
    credit = fields.Boolean(
        'Credit', help="Check this if you want to create Fuel Vouchers for \
        this line"),
    fuel_supplier_id = fields.Many2one(
        'res.partner', 'Fuel Supplier',
        domain=[('tms_category', '=', 'fuel')], required=False)
    # Estos campos se crearon para generar automaticamente las facturas de
    # los gastos que asi sean.
    is_invoice = fields.Boolean('Is Invoice?')
    partner_id = fields.Many2one('res.partner', 'Supplier')
    invoice_date = fields.Date('Date')
    invoice_number = fields.Char('Invoice Number', size=64)
    invoice_id = fields.Many2one(
        'account.invoice', 'Supplier Invoice', readonly=True)

    def on_change_product_id(self, product_id):
        res = {}
        if not product_id:
            return {}
        prod_obj = self.pool.get('product.product')
        for product in prod_obj.browse([product_id], context=None):
            res = {'value': {
                'product_uom': product.uom_id.id,
                'name': product.name,
                'tax_id': [(6, 0, [x.id for x in product.supplier_taxes_id])],
            }}
        return res

    def on_change_price_total(
            self, product_id, product_uom_qty,
            price_total, special_tax_amount):
        res = {}
        if not (product_uom_qty and product_id and price_total):
            return res
        tax_factor = 0.00
        prod_obj = self.pool.get('product.product')
        for line in prod_obj.browse(
                [product_id], context=None)[0].supplier_taxes_id:
            tax_factor = ((tax_factor + line.amount)
                          if line.amount != 0.0 else tax_factor)
        price_unit = price_total / (1.0 + tax_factor) / product_uom_qty
        price_subtotal = price_unit * product_uom_qty
        tax_amount = price_subtotal * tax_factor + special_tax_amount
        res = {'value': {
            'price_unit': price_unit,
            'price_unit_control': price_unit,
            'price_subtotal': price_subtotal,
            'tax_amount': tax_amount,
        }}
        return res

    def on_change_qty(self, product_id, product_uom_qty, price_unit):
        res = {}
        if not (product_uom_qty and product_id and price_unit):
            return res
        tax_factor = 0.00
        prod_obj = self.pool.get('product.product')
        for line in prod_obj.browse(
                [product_id], context=None)[0].supplier_taxes_id:
            tax_factor = ((tax_factor + line.amount)
                          if line.amount != 0.0 else tax_factor)
        price_total = price_unit * (1.0 + tax_factor) * product_uom_qty
        price_subtotal = price_unit * product_uom_qty
        tax_amount = price_subtotal * tax_factor
        res = {'value': {
            'price_unit': price_unit,
            'price_total': price_total,
            'price_subtotal': price_subtotal,
            'tax_amount': tax_amount,
        }}
        return res

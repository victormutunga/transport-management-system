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
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_waybill_info(self):
        res = {}
        for invoice in self.browse(self):
            waybill_rate = invoice_positive_taxes = invoice_negative_taxes = 0
            product = ''
            arrival_id = departure_id = unit_id = False
            for waybill in invoice.waybill_ids:
                product = waybill.waybill_shipped_product[
                    0].product_id.name.split(' ')[0]
                arrival_id = waybill.travel_id.route_id.arrival_id.id
                departure_id = waybill.travel_id.route_id.departure_id.id
                unit_id = waybill.unit_id.id
                for factor in waybill.waybill_customer_factor:
                    waybill_rate = (factor.factor if factor.factor_type ==
                                    'weight' else factor.fixed_amount)
                    continue
                continue
            for taxes in invoice.tax_line:
                invoice_positive_taxes += (taxes.amount
                                           if taxes.amount > 0.0
                                           else 0.0)
                invoice_negative_taxes += (taxes.amount
                                           if taxes.amount < 0.0
                                           else 0.0)
            res[invoice.id] = {
                'product': product,
                'waybill_rate': waybill_rate,
                'departure_id': departure_id,
                'arrival_id': arrival_id,
                'unit_id': unit_id,
                'invoice_positive_taxes_sum': invoice_positive_taxes,
                'invoice_negative_taxes_sum': invoice_negative_taxes,
            }
        return res

    tms_type = fields.Selection(
        [('none', 'N/A'), ('waybill', 'Waybill'), ('invoice', 'Invoice'), ],
        'TMS Type', help="Waybill -> This invoice results from one Waybill \
        (Mexico - Carta Porte/Guia con valor fiscal)\nInvoice -> This Invoice \
        results from several Waybills (México - Carta Porte/Guia sin valor \
        Fiscal)", require=False, default=None)
    waybill_ids = fields.One2many(
        'tms.waybill', 'invoice_id', 'Waybills', readonly=True,
        required=False)
    departure_address_id = fields.Many2one(
        'res.partner', 'Departure Address', readonly=True, required=False)
    arrival_address_id = fields.Many2one(
        'res.partner', 'Arrival Address', readonly=True, required=False)
    expense_ids = fields.One2many(
        'tms.expense', 'invoice_id', 'Travel Expenses', readonly=True,
        required=False)
    fuelvoucher_ids = fields.One2many(
        'tms.fuelvoucher', 'invoice_id', 'Fuel Vouchers', readonly=True,
        required=False)
    travel_id = fields.Many2one(
        'tms.travel', 'Travel', readonly=True, required=False)
    vehicle_id = fields.Many2one(
        'fleet.vehicle', 'Vehicle', readonly=True, required=False)
    employee_id = fields.Many2one(
        'hr.employee', 'Driver', readonly=True, required=False)
    waybill_shipped_ids = fields.One2many(
        'tms.waybill.shipped_grouped',
        'invoice_id', 'Group Shipped Qty by Product',
        readonly=True, required=False)
#   'product': fields.function(_get_waybill_info, string='Product',
#   type='char',  size='128', multi=True, method=True),
    waybill_rate = fields.Float(
        compute=_get_waybill_info, string='Waybill Rate',
        digits_compute=dp.get_precision('Sale Price'), multi=True,
        method=True)
    departure_id = fields.Many2one(
        compute=_get_waybill_info, string='Departure',
        relation='tms.place', multi=True, method=True)
    arrival_id = fields.Many2one(
        compute=_get_waybill_info, string='Arrival',
        relation='tms.place', multi=True, method=True)
    unit_id = fields.Many2one(
        compute=_get_waybill_info, string='Unit',
        relation='fleet.vehicle', multi=True, method=True)
    invoice_positive_taxes_sum = fields.Float(
        compute=_get_waybill_info, string='Positive Taxes',
        digits_compute=dp.get_precision('Sale Price'), multi=True,
        method=True)
    invoice_negative_taxes_sum = fields.Float(
        compute=_get_waybill_info, string='Negative Taxes',
        digits_compute=dp.get_precision('Sale Price'), multi=True,
        method=True)

    def unlink(self):
        # if context is None:
        #     context = {}
        invoices = self.read(['state', 'internal_number', 'origin'])
        for invoice in invoices:
            if (invoice['state'] in ('draft', 'cancel') and
                    invoice['internal_number'] is not False and
                    invoice['origin'] == 'TMS-Fuel Voucher'):
                self.write({'internal_number': False})
        return super(AccountInvoice, self).unlink(self)

    def action_cancel_draft(self):
        for invoice in self.browse():
            if invoice.waybill_ids:
                raise models.except_osv(
                    _('Warning!'),
                    _("You can not Set to Draft an Invoice \
                        created from Waybills!"))
        return super(AccountInvoice, self).action_cancel_draft(self)

#    def action_move_create(self, cr, uid, ids, context=None):
#        res = super(account_invoice, self).action_move_create(cr, uid, ids,
#         context=context)
#        move_line_obj = self.pool.get('account.move.line')
#        for invoice in self.browse(cr, uid, ids):
#            lines = move_line_obj.search(cr, uid, [('move_id','=',
#         invoice.move_id.id)])
#            if invoice.vehicle_id.id:
#                move_line_obj.write(cr, uid, lines, {'vehicle_id':
#         invoice.vehicle_id.id})
#            if invoice.employee_id.id:
#                move_line_obj.write(cr, uid, lines, {'employee_id':
#         invoice.employee_id.id})
#        return res

    @api.multi
    def line_get_convert(self, line, part):
        res = super(AccountInvoice, self).line_get_convert(line, part)
        res.update({
            'vehicle_id': self.pool.get('vehicle_id', False),
            'employee_id': self.pool.get('employee_id', False),
            'sale_shop_id': self.pool.get('sale_shop_id', False),
        })
        return res

    def _get_analytic_lines(self):
        inv = self.browse(id)
        cur_obj = self.pool.get('res.currency')

        company_currency = self.pool['res.company'].browse(
            inv.company_id.id).currency_id.id
        if inv.type in ('out_invoice', 'in_refund'):
            sign = 1
        else:
            sign = -1

        iml = self.pool.get('account.invoice.line').move_line_get(
            inv.id)
        for il in iml:
            if not il['account_id'] or il['account_id'] is None:
                il['account_id'] = il['account_id2']
            if il['account_analytic_id']:
                if inv.type in ('in_invoice', 'in_refund'):
                    ref = inv.reference
                else:
                    ref = self._convert_ref(inv.number)
                if not inv.journal_id.analytic_journal_id:
                    raise models.except_osv(_(
                        'No Analytic Journal!'),
                        _("You have to define an analytic journal on \
                            the '%s' journal!") % (inv.journal_id.name,))
                il['analytic_lines'] = [(0, 0, {
                    'name': il['name'],
                    'date': inv['date_invoice'],
                    'account_id': il['account_analytic_id'],
                    'unit_amount': il['quantity'],
                    'amount': cur_obj.compute(
                        inv.currency_id.id, company_currency, il['price'],
                        context={'date': inv.date_invoice}) * sign,
                    'product_id': il['product_id'],
                    'product_uom_id': il['uos_id'],
                    'general_account_id': il['account_id'],
                    'journal_id': inv.journal_id.analytic_journal_id.id,
                    'ref': ref,
                })]
        return iml

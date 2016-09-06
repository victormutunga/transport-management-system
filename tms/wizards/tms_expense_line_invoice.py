# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, models


class TmsExpenseLineInvoice(models.TransientModel):

    """ To create payment for Waybill"""

    _name = 'tms.expense.line.invoice'
    _description = 'Make Payment for Expense lines'

    @api.multi
    def make_expense_line_invoices(self):
        active_ids = self.env['tms.expense.line'].browse(
            self._context.get('active_ids'))
        if not active_ids:
            return {}
        for expense in active_ids:
            expense.invoice_id = self.env['account.invoice'].create({
                'partner_id': expense.partner_id.id,
                'fiscal_position_id': (
                    expense.partner_id.property_account_position_id.id),
                'reference': expense.name,
                'currency_id': expense.currency_id.id,
                'account_id': (
                    expense.partner_id.property_account_payable_id.id),
                'type': 'out_invoice',
                'invoice_line_ids': (0, 0, {
                    'product_id': expense.product_id.id,
                    'quantity': expense.product_qty,
                    'price_unit': expense.price_subtotal,
                    'invoice_line_tax_ids': [(
                        6, 0,
                        [x.id for x in expense.tax_ids]
                        )],
                    'name': expense.name,
                    'account_id': expense.account_id.id,
                    }),
                })
            expense.write({'invoice_id': expense.invoice_id.id})

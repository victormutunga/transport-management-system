
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

from openerp import models
from openerp.tools.translate import _

# Wizard que permite generar el pago de la liquidación


class TmsExpensePayment(models.TransientModel):

    """ To create payment for expense"""

    _name = 'tms.expense.payment'
    _description = 'Make Payment for Travel Expenses'

    def make_payment(self, cr, uid, ids, context=None):
        if context is None:
            record_ids = ids
        else:
            record_ids = context.get('active_ids', [])
        if not record_ids:
            return []
        ids = record_ids
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(
            'account_voucher', 'view_vendor_receipt_dialog_form')
        cr.execute("select count(distinct(employee_id, currency_id)) from \
            tms_expense where state in ('confirmed') and id \
            IN %s", (tuple(ids),))
        xids = filter(None, map(lambda x: x[0], cr.fetchall()))
        if len(xids) > 1:
            raise Warning(
                'Error !',
                'You can not create Payment for several Drivers and or \
                distinct currency...')
        amount = 0.0
        move_line_ids = []
        expense_names = ""
        for expense in self.pool.get('tms.expense').browse(self):
            if (expense.state == 'confirmed' and
                    expense.amount_balance > 0.0 and not expense.paid):
                expense_names += ", " + expense.name
                amount += expense.amount_balance
                for move_line in expense.move_id.line_id:
                    if (move_line.credit > 0.0 and
                            expense.employee_id.address_home_id.property_account_payable.id ==
                            move_line.account_id.id):
                        move_line_ids.append(move_line.id)
        if not amount:
            raise Warning(
                'Warning !',
                'All Travel Expenses are already paid or are not in Confirmed \
                State...')
        res = {
            'name': _("Travel Expense Payment"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'payment_expected_currency': expense.currency_id.id,
                'default_partner_id':
                self.pool.get('res.partner')._find_accounting_partner(
                    expense.employee_id.address_home_id).id,
                'default_amount': amount,
                'default_name': _('Travel Expense(s) %s') % (expense_names),
                'close_after_process': False,
                'move_line_ids': [x for x in move_line_ids],
                'default_type': 'payment',
                'type': 'payment'
            }}

        return res

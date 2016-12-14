# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import _, api, exceptions, models


class TmsExpensePayment(models.TransientModel):

    """ To create payment for Expense"""

    _name = 'tms.expense.payment'
    _description = 'Make Payment for Expense'

    @api.multi
    def make_payment(self):
        active_ids = self.env['tms.expense'].browse(
            self._context.get('active_ids'))
        if not active_ids:
            return {}

        partner_ids = []
        total = 0.0
        expense_names = ''
        control = 0
        for expense in active_ids:
            if expense.state in ('confirmed', 'closed') and not expense.paid:
                if not expense.employee_id.address_home_id.id:
                    raise exceptions.ValidationError(
                        _('You must configure the home address for the'
                            ' driver.'))
                partner_ids.append(expense.employee_id.address_home_id.id)
                currency = expense.currency_id
                total += currency.compute(expense.amount_balance,
                                          self.env.user.currency_id)
                expense_names += ' ' + expense.name + ', '
            else:
                raise exceptions.ValidationError(
                    _('The expenses must be in confirmed / closed state'
                      ' and unpaid.'))

        for partner_id in partner_ids:
            if control == 0:
                old_partner = partner_id
                current_partner = partner_id
                control = 1
            else:
                current_partner = partner_id
            if old_partner != current_partner:
                raise exceptions.ValidationError(
                    _('The expenses must be of the same driver. '
                        'Please check it.'))
            else:
                old_partner = partner_id

        res = {
            'name': _('Driver Expense Payment'),
            'view_mode': 'form',
            'view_id': self.env.ref(
                'account.view_account_payment_form').id,
            'view_type': 'form',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_communication': _(
                    'Expense(s): ' + expense_names + ' payment.'),
                'default_currency_id': self.env.user.currency_id.id,
                'default_partner_id': old_partner,
                'default_amount': total,
                'default_name': expense_names,
                'default_expense_ids': [id for id in active_ids.ids],
                'default_payment_type': 'outbound',
                'close_after_process': False,
                'default_type': 'payment',
                'type': 'payment'
            }
        }
        return res

# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import _, api, exceptions, models


class TmsExpenseInvoice(models.TransientModel):

    """ To create invoice for each Expense"""

    _name = 'tms.expense.invoice'
    _description = 'Make Invoices from Expense Records'

    @api.multi
    def make_invoices(self):
        active_ids = self.env['tms.expense'].browse(
            self._context.get('active_ids'))
        if not active_ids:
            return {}
        # invoice_obj = self.env['account.invoice']
        partner_ids = []
        total = 0.0
        expense_names = ''
        control = 0
        for expense in active_ids:
            if expense.state == 'confirmed':
                if not expense.employee_id.address_home_id.id:
                    raise exceptions.ValidationError(
                        _('You must configure the home address for the'
                            ' driver.'))
                partner_ids.append(expense.employee_id.address_home_id.id)
                currency = expense.currency_id
                total += currency.compute(expense.amount_total_subtotal,
                                          self.env.user.currency_id)
                expense_names += ' ' + expense.name + ', '
                # expense_journal = expense.base_id.expense_journal_id.id
            else:
                raise exceptions.ValidationError(
                    _('The expense must be in confirmed state'))

        for partner_id in partner_ids:
            if control == 0:
                old_partner = partner_id
                current_partner = partner_id
                control = 1
            else:
                current_partner = partner_id
            if old_partner != current_partner:
                raise exceptions.ValidationError(
                    _('The advances must be of the same driver. '
                        'Please check it.'))
            else:
                old_partner = partner_id

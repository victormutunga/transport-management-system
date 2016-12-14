# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import _, api, exceptions, models


class TmsAdvancePayment(models.TransientModel):

    """ To create payment for Advance"""

    _name = 'tms.advance.payment'
    _description = 'Make Payment for Advances'

    @api.multi
    def make_payment(self):
        active_ids = self.env['tms.advance'].browse(
            self._context.get('active_ids'))
        if not active_ids:
            return {}

        partner_ids = []
        total = 0.0
        advance_names = ''
        control = 0
        operating_unit_id = False
        for advance in active_ids:
            if advance.state in ('confirmed', 'closed') and not advance.paid:
                if not advance.employee_id.address_home_id.id:
                    raise exceptions.ValidationError(
                        _('You must configure the home address for the'
                            ' driver.'))
                partner_ids.append(advance.employee_id.address_home_id.id)
                currency = advance.currency_id
                total += currency.compute(advance.amount,
                                          self.env.user.currency_id)
                advance_names += ' ' + advance.name + ', '
                operating_unit_id = advance.operating_unit_id.id
            else:
                raise exceptions.ValidationError(
                    _('The advances must be in confirmed / closed state'
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
                    _('The advances must be of the same driver. '
                        'Please check it.'))
            else:
                old_partner = partner_id

        res = {
            'name': _('Driver Advance Payment'),
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
                    'Advance(s): ' + advance_names + ' payment.'),
                'default_currency_id': self.env.user.currency_id.id,
                'default_partner_id': old_partner,
                'default_amount': total,
                'default_name': advance_names,
                'default_advance_ids': [id for id in active_ids.ids],
                'default_payment_type': 'outbound',
                'default_operating_unit_id': operating_unit_id,
                'close_after_process': False,
                'default_type': 'payment',
                'type': 'payment'
            }
        }
        return res

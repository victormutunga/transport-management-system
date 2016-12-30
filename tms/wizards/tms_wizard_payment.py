# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import _, api, fields, models
from openerp.exceptions import ValidationError


class TmsWizardPayment(models.TransientModel):
    _name = 'tms.wizard.payment'

    journal_id = fields.Many2one(
        'account.journal', string='Bank Account',
        domain="[('type', '=', 'bank')]")
    amount_total = fields.Float(compute='_compute_amount_total')

    @api.depends('journal_id')
    def _compute_amount_total(self):
        for rec in self:
            amount_total = 0
            currency = rec.journal_id.currency_id or self.env.user.currency_id
            active_ids = self.env[self._context.get('active_model')].browse(
                self._context.get('active_ids'))
            for obj in active_ids:
                if self._context.get('active_model') == 'tms.advance':
                    amount_total += currency.compute(
                        obj.amount, self.env.user.currency_id)
                elif self._context.get('active_model') == 'tms.expense':
                    amount_total += currency.compute(
                        obj.amount_balance, self.env.user.currency_id)
            rec.amount_total = amount_total

    @api.multi
    def make_payment(self):
        for rec in self:
            active_ids = self.env[self._context.get('active_model')].browse(
                self._context.get('active_ids'))
            bank_account_id = rec.journal_id.default_debit_account_id.id
            currency = rec.journal_id.currency_id or self.env.user.currency_id
            for obj in active_ids:
                if obj.state != 'confirmed' or obj.paid:
                    raise ValidationError(
                        _('The document %s must be confirmed and '
                          'unpaid.') % obj.name)
                move_lines = []
                move_line = {
                    'name': _('Payment'),
                    'ref': obj.name,
                    'account_id': bank_account_id,
                    'debit': 0.0,
                    'journal_id': rec.journal_id.id,
                    'partner_id': obj.employee_id.address_home_id.id,
                    'operating_unit_id': obj.operating_unit_id.id,
                }
                counterpart_move_line = {
                    'name': _('Payment'),
                    'ref': obj.name,
                    'account_id': (
                        obj.employee_id.address_home_id.
                        property_account_payable_id.id),
                    'credit': 0.0,
                    'journal_id': rec.journal_id.id,
                    'partner_id': obj.employee_id.address_home_id.id,
                    'operating_unit_id': obj.operating_unit_id.id,
                }
                if self._context.get('active_model') == 'tms.advance':
                    if currency.id != obj.currency_id.id:
                        move_line['amount_currency'] = obj.amount * -1
                        move_line['currency_id'] = currency.id
                        move_line['credit'] = currency.compute(
                            obj.amount, self.env.user.currency_id)
                        counterpart_move_line['amount_currency'] = obj.amount
                        counterpart_move_line['currency_id'] = currency.id
                        counterpart_move_line['debit'] = currency.compute(
                            obj.amount, self.env.user.currency_id)
                    else:
                        move_line['credit'] = obj.amount
                        counterpart_move_line['debit'] = obj.amount
                elif self._context.get('active_model') == 'tms.expense':
                    if obj.amount_balance < 0.0:
                        raise ValidationError(
                            _('You cannot pay the expense %s because the '
                              'balance is negative') % obj.name)
                    if currency.id != obj.currency_id.id:
                        move_line['amount_currency'] = obj.amount_balance * -1
                        move_line['currency_id'] = currency.id
                        move_line['credit'] = currency.compute(
                            obj.amount_balance, self.env.user.currency_id)
                        counterpart_move_line['amount_currency'] = (
                            obj.amount_balance)
                        counterpart_move_line['currency_id'] = currency.id
                        counterpart_move_line['debit'] = currency.compute(
                            obj.amount_balance, self.env.user.currency_id)
                    else:
                        move_line['credit'] = obj.amount_balance
                        counterpart_move_line['debit'] = obj.amount_balance
                move_lines.append((0, 0, move_line))
                move_lines.append((0, 0, counterpart_move_line))
                move = {
                    'date': fields.Date.today(),
                    'journal_id': rec.journal_id.id,
                    'ref': obj.name,
                    'line_ids': [line for line in move_lines],
                    'operating_unit_id': obj.operating_unit_id.id
                }
                move_id = self.env['account.move'].create(move)
                move_ids = []
                for move_line in move_id.line_ids:
                    if move_line.account_id.internal_type == 'payable':
                        move_ids.append(move_line.id)
                for move_line in obj.move_id.line_ids:
                    if (move_line.account_id.internal_type == 'payable' and
                            'Positive Balance' in move_line.name):
                        move_ids.append(move_line.id)
                reconcile_ids = self.env['account.move.line'].browse(move_ids)
                reconcile_ids.reconcile()
                obj.payment_move_id = move_id

# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def process_reconciliation(
            self, counterpart_aml_dicts=None, payment_aml_rec=None,
            new_aml_dicts=None):
        for rec in self:
            res = super(AccountBankStatementLine, rec).process_reconciliation(
                counterpart_aml_dicts, payment_aml_rec, new_aml_dicts)
            advances = False
            expenses = False
            loans = False
            debit_payment_lines = res.line_ids.filtered(
                lambda x: x.account_id.user_type_id.id != 3)
            for lines in debit_payment_lines:
                payment_line = (
                    lines.full_reconcile_id.
                    reconciled_line_ids.filtered(
                        lambda x: x.journal_id.type != 'bank'))
                if len(payment_line) == 1:
                    advances = self.env['tms.advance'].search(
                        [('move_id', '=', payment_line.move_id.id)])
                    expenses = self.env['tms.expense'].search(
                        [('move_id', '=', payment_line.move_id.id)])
                    loans = self.env['tms.expense.loan'].search(
                        [('move_id', '=', payment_line.move_id.id)])
                if advances:
                    for advance in advances:
                        advance.paid = True
                        advance.payment_move_id = res.id
                if expenses:
                    for expense in expenses:
                        expense.paid = True
                        expense.payment_move_id = res.id
                if loans:
                    for loan in loans:
                        loan.paid = True
                        loan.payment_move_id = res.id

            return res

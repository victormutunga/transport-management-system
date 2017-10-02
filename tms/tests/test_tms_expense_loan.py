# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestTmsExpenseLoan(TransactionCase):

    def setUp(self):
        super(TestTmsExpenseLoan, self).setUp()
        self.expense_loan = self.env['tms.expense.loan']
        self.operating_unit = self.env.ref(
            'operating_unit.main_operating_unit')
        self.employee_id = self.env.ref('tms.tms_hr_employee_01')
        obj_account = self.env['account.account']
        account_bank = obj_account.create({
            "code": 'X031216',
            "name": 'Advance',
            "user_type_id": self.env.ref(
                "account.data_account_type_current_assets").id
        })
        self.journal_id = self.env['account.journal'].create({
            'name': 'Test Bank',
            'type': 'bank',
            'code': 'TESTBANK',
            'default_debit_account_id': account_bank.id,
            'default_credit_account_id': account_bank.id,
        })

    def create_expense_loan(self):
        return self.expense_loan.create({
            "operating_unit_id": self.operating_unit.id,
            "employee_id": self.employee_id.id,
            "product_id": self.env.ref('tms.product_loan').id,
            "amount": 100.00,
            "discount_type": "fixed",
            "discount_method": "each"
        })

    def test_10_tms_expense_loan_create(self):
        self.operating_unit.loan_sequence_id = False
        with self.assertRaisesRegexp(
                ValidationError, 'You need to define the sequence for loans '
                'in base Mexico'):
            self.create_expense_loan()

    def test_20_tms_expense_loand_action_authorized(self):
        loan = self.create_expense_loan()
        loan.action_authorized()
        self.assertEqual(loan.state, 'approved')

    def test_30_tms_expense_loan_action_approve(self):
        loan = self.create_expense_loan()
        msg = ('Could not approve the Loan. The Amount of discount must be '
               'greater than zero.')
        with self.assertRaisesRegexp(ValidationError, msg):
            loan.action_approve()
        loan.discount_type = 'percent'
        with self.assertRaisesRegexp(ValidationError, msg):
            loan.action_approve()

    def test_40_tms_expense_loan_action_cancel(self):
        loan = self.create_expense_loan()
        loan.fixed_discount = 10.0
        loan.action_approve()
        loan.action_confirm()
        loan.move_id.post()
        wizard = self.env['tms.wizard.payment'].with_context({
            'active_model': 'tms.expense.loan',
            'active_ids': [loan.id]}).create({
                'journal_id': self.journal_id.id,
                'amount_total': loan.amount,
            })
        wizard.make_payment()
        with self.assertRaisesRegexp(
                ValidationError,
                'Could not cancel this loan because'
                ' the loan is already paid. '
                'Please cancel the payment first.'):
            loan.action_cancel()

    def test_50_tms_expense_loan_action_confirm(self):
        loan = self.create_expense_loan()
        loan.employee_id.tms_loan_account_id = False
        with self.assertRaisesRegexp(
                ValidationError,
                'Warning! You must have configured the accounts of the tms'):
            loan.action_confirm()

    def test_60_tms_expense_loan_unlink(self):
        loan = self.create_expense_loan()
        loan.fixed_discount = 10.0
        loan.action_approve()
        loan.action_confirm()
        loan.move_id.post()
        loan.move_id.journal_id.update_posted = True
        with self.assertRaisesRegexp(
                ValidationError,
                'You can not delete a Loan in status confirmed or closed'):
            loan.unlink()
        loan.action_cancel()
        loan.action_cancel_draft()
        loan.unlink()

    # def test_70_tms_expense_loan_compute_balance(self):
    #     loan = self.create_expense_loan()
    #     loan.fixed_discount = 50.0
    #     loan.expense_ids.create({
    #         })

# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
# from test_tms_expense_line import create_expense


class TestTmsExpense(TransactionCase):

    def setUp(self):
        super(TestTmsExpense, self).setUp()
        self.tms_expense = self.env['tms.expense']
        self.tms_expense_line = self.env['tms.expense.line']

        self.get_initial_data()
        self.confirm_advances()
        self.expense = self.create_expense()

        # Confirm expense.
        self.expense.action_approved()
        self.expense.action_confirm()

        # Allow to cancel the expense
        journal = self.env.ref('tms.tms_account_journal_expense')
        journal.write({'update_posted': True})
        # Then cancel expense
        self.expense.action_cancel()

    def get_initial_data(self):
        self.product_fuel = self.env.ref('tms.product_fuel')
        self.operating_unit = self.env.ref(
            'operating_unit.main_operating_unit')
        self.unit = self.env.ref('tms.tms_fleet_vehicle_01')
        self.driver = self.env.ref('tms.tms_hr_employee_01')

        self.driver.write({
            'address_home_id': self.env.ref(
                'base.res_partner_address_31').id,
            'tms_advance_account_id': self.env.ref(
                'l10n_generic_coa.1_conf_xfa').id,
            'tms_expense_negative_account_id': self.env.ref(
                'l10n_generic_coa.1_conf_stk').id})

        self.travel = self.env.ref('tms.tms_travel_01')
        self.bank_account = self.env['account.journal'].create({
            'bank_acc_number': '121212',
            'name': 'Bank(MXN)',
            'code': '1212',
            'type': 'bank',
            'currency_id': self.env.ref('base.MXN').id,
        })

    def confirm_advances(self):
        # Confirm and paid advances.
        self.travel.advance_ids.action_approve()
        self.travel.advance_ids.action_authorized()
        self.travel.advance_ids.action_confirm()

        self.env['tms.wizard.payment'].with_context({
            'active_ids': self.travel.advance_ids.mapped('id'),
            'active_model': 'tms.advance',
        }).create({
            'amount_total': sum(self.travel.advance_ids.mapped('amount')),
            'date': '03/09/2018',
            'journal_id': self.bank_account.id,
        }).make_payment()

    def create_expense(self):
        return self.tms_expense.create({
            'operating_unit_id': self.operating_unit.id,
            'unit_id': self.unit.id,
            'employee_id': self.driver.id,
            'travel_ids': [(4, self.travel.id)],
            'expense_line_ids': [(0, 0, {
                'travel_id': self.travel.id,
                'product_id': self.product_fuel.id,
                'name': self.product_fuel.name,
                'line_type': self.product_fuel.tms_product_category,
                'unit_price': 100.0,
                'partner_id': self.env.ref('base.res_partner_address_12').id,
                'invoice_number': '10010101',
                'date': '03/08/2018',
            })]
        })

    def test_10_tms_expense_action_confirm(self):
        fuel_line_ids = self.expense.fuel_log_ids.filtered(
            lambda x: x.created_from_expense).mapped('expense_line_id')
        line_ids = self.expense.expense_line_ids.filtered(
            lambda x: x.expense_fuel_log).mapped('id')
        for lid in line_ids:
            if lid not in fuel_line_ids.mapped('id'):
                ValidationError(
                    'Fuel Line was not created or asigned to the expense')

    def test_20_tms_expense_action_cancel(self):
        if self.expense.expense_line_ids.filtered(
                lambda x: x.expense_fuel_log):
            if self.expense.fuel_log_ids.filtered(
                    lambda x: x.created_from_expense):
                ValidationError(
                    'There should not be fuel log lines created from expense')

# -*- coding: utf-8 -*-
# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestTmsExpense(TransactionCase):

    def setUp(self):
        super(TestTmsExpense, self).setUp()
        self.tms_expense = self.env['tms.expense']
        self.tms_expense_line = self.env['tms.expense.line']
        self.tms_advance = self.env['tms.advance']
        self.tms_travel = self.env['tms.travel']
        self.tms_log_fuel = self.env['fleet.vehicle.log.fuel']

        # Get initial data
        self.product_fuel = self.env.ref('tms.product_fuel')
        self.product_real_expense = self.env.ref('tms.product_real_expense')
        self.operating_unit = self.env.ref(
            'operating_unit.main_operating_unit')
        self.unit = self.env.ref('tms.tms_fleet_vehicle_05')
        self.driver = self.env.ref('tms.tms_hr_employee_02')
        employee_accont = self.env['account.account'].create({
            "code": 'TestEmployee',
            "name": 'Test Employee',
            "user_type_id": self.env.ref(
                "account.data_account_type_current_assets").id
        })
        self.driver.write({
            'address_home_id': self.env.ref(
                'base.res_partner_address_31').id,
            'tms_advance_account_id': employee_accont.id,
            'tms_expense_negative_account_id': employee_accont.id})

        self.travel = self.env.ref('tms.tms_travel_05')

        # Create advance
        self.tms_advance.create({
            'operating_unit_id': self.operating_unit.id,
            'travel_id': self.travel.id,
            'date': '03/07/2018',
            'product_id': self.product_real_expense.id,
            'amount': 350.00,
        })
        # Confirm fuel vouchers
        self.travel.fuel_log_ids.action_approved()
        self.travel.fuel_log_ids.action_confirm()
        # Confirm and paid advances.
        self.bank_account = self.env['account.journal'].create({
            'bank_acc_number': '121212',
            'name': 'Test Bank',
            'type': 'bank',
            'code': 'TESTBANK',
        })
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

        # Confirm travel
        self.travel.action_progress()
        self.travel.action_done()

        # Allow to cancel the expense
        journal = self.env.ref('tms.tms_account_journal_expense')
        journal.write({'update_posted': True})

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

    def test_10_tms_expense_create_advance_line(self):
        adv = self.tms_advance.create({
            'operating_unit_id': self.operating_unit.id,
            'travel_id': self.travel.id,
            'unit_id': self.unit.id,
            'employee_id': self.driver.id,
            'product_id': self.product_real_expense.id,
            'amount': 10.0,
        })
        with self.assertRaises(ValidationError) as err:
            self.create_expense()
        self.assertEquals(
            err.exception.name,
            'Oops! All the advances must be confirmed or cancelled \n '
            'Name of advance not confirmed or cancelled: ' + adv.name +
            '\n State: ' + adv.state)
        adv.action_approve()
        adv.action_authorized()
        adv.action_confirm()
        with self.assertRaises(ValidationError) as err2:
            self.create_expense()
        self.assertEquals(
            err2.exception.name,
            'Oops! All the advances must be paid\n '
            'Name of advance not paid: ' + adv.name)

    def test_20_tms_expense_create_fuel_line(self):
        log = self.tms_log_fuel.create({
            'operating_unit_id': self.operating_unit.id,
            'vendor_id': self.env.ref('base.res_partner_1').id,
            'travel_id': self.travel.id,
            'vehicle_id': self.unit.id,
            'product_id': self.product_fuel.id,
            'tax_amount': 10.0,
            'price_total': 100.0,
        })
        with self.assertRaises(ValidationError) as err:
            self.create_expense()
        self.assertEquals(
            err.exception.name,
            'Oops! All the voucher must be confirmed\n '
            'Name of voucher not confirmed: ' + log.name + '\n '
            'State: ' + log.state)

    def test_30_tms_expense_create(self):
        travel_ids = self.tms_travel.search([
            ('employee_id', '=', self.driver.id),
            ('unit_id', '=', self.unit.id),
            ('state', '=', 'done'),
        ]).mapped('id')
        self.assertTrue(self.travel.id in travel_ids)
        self.create_expense()

    def test_40_tms_expense_action_approved(self):
        pass

    def test_50_tms_expense_action_confirm(self):
        expense = self.create_expense()
        # Confirm expense.
        expense.action_approved()
        expense.action_confirm()

        fuel_line_ids = expense.fuel_log_ids.filtered(
            lambda x: x.created_from_expense).mapped('expense_line_id')
        line_ids = expense.expense_line_ids.filtered(
            lambda x: x.expense_fuel_log).mapped('id')
        for lid in line_ids:
            self.assertTrue(lid in fuel_line_ids.mapped('id'))

    def test_60_tms_expense_action_cancel(self):
        expense = self.create_expense()
        # Confirm expense.
        expense.action_approved()
        expense.action_confirm()
        # Then cancel expense
        expense.action_cancel()

        if expense.expense_line_ids.filtered(
                lambda x: x.expense_fuel_log):
            self.assertFalse(any(expense.fuel_log_ids.filtered(
                    lambda x: x.created_from_expense)))

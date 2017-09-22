# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestTmsExpenseLine(TransactionCase):

    def setUp(self):
        super(TestTmsExpenseLine, self).setUp()
        self.expense = self.env['tms.expense']
        self.expense_line = self.env['tms.expense.line']
        self.product = self.env.ref('tms.product_madeup')
        self.product_fuel = self.env.ref('tms.product_fuel')
        self.operating_unit = self.env.ref(
            'operating_unit.main_operating_unit')
        self.unit = self.env.ref('tms.tms_fleet_vehicle_01')
        self.driver = self.env.ref('tms.tms_hr_employee_01')
        obj_account = self.env['account.account']
        advance = obj_account.create({
            "code": 'X031216',
            "name": 'Advance',
            "user_type_id": self.env.ref(
                "account.data_account_type_current_assets").id
        })
        balance = obj_account.create({
            "code": 'X190217',
            "name": 'Balance',
            "user_type_id": self.env.ref(
                "account.data_account_type_current_assets").id
        })
        self.driver.write({
            'address_home_id': self.env.ref(
                'base.res_partner_address_31').id,
            'tms_advance_account_id': advance.id,
            'tms_expense_negative_account_id': balance.id})
        self.advance_1 = self.env.ref(
            'tms.tms_advance_01').state = 'confirmed'
        self.advance_2 = self.env.ref(
            'tms.tms_advance_02').state = 'confirmed'

    def create_expense(self):
        expense = self.expense.create({
            'operating_unit_id': self.operating_unit.id,
            'unit_id': self.unit.id,
            'employee_id': self.driver.id,
            'expense_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'name': self.product.name,
                'line_type': self.product.tms_product_category})]
        })
        return expense

    def test_10_tms_expense_line_onchange_product_id(self):
        expense = self.create_expense()
        expense.expense_line_ids.write({
            'product_id': self.product_fuel.id,
        })
        expense_line = expense.expense_line_ids
        expense_line._onchange_product_id()
        self.assertEqual(
            expense_line.tax_ids, self.product_fuel.supplier_taxes_id)
        self.assertEqual(
            expense_line.line_type, self.product_fuel.tms_product_category)
        self.assertEqual(
            expense_line.product_uom_id.id, self.product_fuel.uom_id.id)
        self.assertEqual(
            expense_line.name, self.product_fuel.name)

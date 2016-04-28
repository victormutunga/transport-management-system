# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError


class TestProductProduct(TransactionCase):
    """
    This will test model product product
    """

    def setUp(self):
        """
        Define global variables
        """
        super(TestProductProduct, self).setUp()
        self.product = self.env['product.product']

    def create_product(self, name, tms_category, type, purchase_ok, sale_ok):
        product = self.product.create({
            'name': name,
            'tms_category': tms_category,
            'type': type,
            'purchase_ok': purchase_ok,
            'sale_ok': sale_ok,
        })
        return product

    def test_10_product_product_onchange_tms_category(self):
        '''
        This test check that method on change tms_category.
        '''
        list_category = [
            ['freight', 'service', False, True],
            ['move', 'service', False, True],
            ['insurance', 'service', False, True],
            ['highway_tolls', 'service', False, True],
            ['other', 'service', False, True],
            ['real_expense', 'service', True, False],
            ['fuel', 'product', True, False],
        ]
        produ = self.create_product(
            'freight', 'freight', 'service', False, True)
        for record in list_category:
            produ.write(
                {'tms_category': record[0],
                 'type': record[1],
                 'purchase_ok': record[2],
                 'sale_ok': record[3]})
            produ._onchange_tms_category()
            self.assertEqual(
                produ.type, record[1], 'On not change works')
            self.assertEqual(
                produ.purchase_ok, record[2], 'On not change works')
            self.assertEqual(
                produ.sale_ok, record[3], 'On not change works')

    def test_20_product_product_check_tms_product(self):
        '''
        This test check that method check tms product
        '''
        for rec in ['freight', 'move', 'insurance', 'highway_tolls', 'other']:
            with self.assertRaisesRegexp(
                ValidationError,
                    'Error! Product is not defined correctly...'):
                self.create_product('freight', rec, 'product', False, True)

    def test_30_product_product_check_tms_product1(self):
        '''
        This test check that method check tms product Real Expense
        '''
        with self.assertRaisesRegexp(
            ValidationError,
                'Error! Real Expense is not defined \
                                correctly...'):
            self.create_product(
                'Product', 'real_expense', 'product', True, False)

    def test_40_product_product_check_tms_product2(self):
        '''
        This test check that method check tms product Fuel
        '''
        with self.assertRaisesRegexp(
            ValidationError,
                'Error! Fuel is not defined correctly...'):
            self.create_product(
                'Product', 'fuel', 'service', True, False)

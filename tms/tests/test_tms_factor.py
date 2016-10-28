# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api
from openerp.tests.common import TransactionCase


class TestTmsFactor(TransactionCase):
    """
    This will test model tms_factor
    """

    def setUp(self):
        """
        Define global variables
        """
        super(TestTmsFactor, self).setUp()
        self.factor = self.env['tms.factor']

    def create_factor(self, name, category, factor_type, factor,
                      fixed_amount):
        factor = self.factor.create({
            'name': name,
            'category': category,
            'factor_type': factor_type,
            'factor': factor,
            'fixed_amount': fixed_amount,
        })
        return factor

    @api.onchange('factor_type')
    def test_10_tms_factor_onchange_factor_type(self):
        '''
        This test check that method on change factor type.
        '''
        factor_type_list = [
            ['', 'name'],
            ['distance', 'Distance Route (Km/Mi)'],
            ['distance_real', 'Distance Real (Km/Mi)'],
            ['weight', 'Weight'],
            ['travel', 'Travel'],
            ['qty', 'Quantity'],
            ['volume', 'Volume'],
            ['percent', 'Income Percent'],
        ]

        factor = self.create_factor(
            'distance', 'driver', 'distance', 12.0, 2)
        for record in factor_type_list:
            factor.write({'factor_type': record[0]})
            factor._onchange_factor_type()
            self.assertEqual(factor.name, record[1], 'On change works')

    def test_20_tms_factor_get_amount(self):
        factor_type_list = [
            ['distance', 'Distance Route (Km/Mi)'],
            ['distance_real', 'Distance Real (Km/Mi)'],
            ['weight', 'Weight'],
            ['travel', 'Travel'],
            ['qty', 'Quantity'],
            ['volume', 'Volume'],
            ['percent', 'Income Percent', True],
            ['percent', 'Income Percent', False],

        ]

        for record in factor_type_list:
            factor = self.create_factor(
                'distance', 'driver', 'distance', 12.0, 2)
            factor.write({'factor_type': record[0]})
            if factor.factor_type == 'distance':
                value = factor.get_amount(12.0, 12.0, 12.0, 12.0, 12.0, 12.0)
                self.assertEqual(
                    value, 144.0,
                    'Get Amount Incorrect factor type(distance)')
            elif factor.factor_type == 'distance_real':
                factor.write({'factor': 0.0})
                value = factor.get_amount(12.0, 12.0, 12.0, 12.0, 12.0, 12.0)
                self.assertEqual(
                    value, 12.0,
                    'Get Amount Incorrect factor type(distance_real)')
            elif factor.factor_type == 'travel':
                value = factor.get_amount(12.0, 12.0, 12.0, 12.0, 12.0, 12.0)
                self.assertEqual(
                    value, 2.0,
                    'Get Amount Incorrect factor type(travel)')
            elif factor.factor_type == 'percent':
                if record[2] is False:
                    value = factor.get_amount(
                        12.0, 12.0, 12.0, 12.0, 12.0, 12.0)
                    self.assertEqual(
                        value, 1.44,
                        'Get Amount Incorrect factor type(percent)mixed False')
                else:
                    factor.write({'mixed': record[2]})
                    value = factor.get_amount(
                        12.0, 12.0, 12.0, 12.0, 12.0, 12.0)
                    self.assertEqual(
                        value, 3.44,
                        'Get Amount Incorrect factor type(percent)mixed True')
            elif factor.factor_type == 'weight':
                factor.write({
                    'range_start': 0.0,
                    'range_end': 24.0,
                })
                value = factor.get_amount(12.0, 12.0, 12.0, 12.0, 12.0, 12.0)
                self.assertEqual(
                    value, 12.0,
                    'Get Amount Incorrect factor type(weight)')
            elif factor.factor_type == 'qty':
                factor.write({
                    'range_start': 0.0,
                    'range_end': 24.0,
                    'mixed': True,
                })
                value = factor.get_amount(12.0, 12.0, 12.0, 12.0, 12.0, 12.0)
                self.assertEqual(
                    value, 146.0,
                    'Get Amount Incorrect factor type(percent)')
            else:
                factor.write({
                    'range_start': 0.0,
                    'range_end': 24.0,
                    'mixed': True,
                    'factor': 0.0
                })
                value = factor.get_amount(12.0, 12.0, 12.0, 12.0, 12.0, 12.0)
                self.assertEqual(
                    value, 2.0,
                    'Get Amount Incorrect factor type(percent)')

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

    def create_factor(self, name, category, factor_type):
        factor = self.factor.create({
            'name': name,
            'category': category,
            'factor_type': factor_type,
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
            'distance', 'driver', 'distance')
        for record in factor_type_list:
            factor.write({'factor_type': record[0]})
            factor._onchange_factor_type()
            self.assertEqual(factor.name, record[1], 'On change works')

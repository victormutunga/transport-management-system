# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import exceptions
from odoo.tests.common import TransactionCase


class TestProductTemplate(TransactionCase):

    def setUp(self):
        super(TestProductTemplate, self).setUp()
        self.product = self.env.ref('tms.product_freight')

    def test_10_product_template_unique_product_per_category(self):
        with self.assertRaises(
                exceptions.ValidationError):
            self.product.write({
                'tms_product_category': 'move'
            })

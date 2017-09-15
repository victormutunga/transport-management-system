# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import exceptions
from openerp.tests.common import TransactionCase


class TestProductTemplate(TransactionCase):

    def setUp(self):
        super(TestProductTemplate, self).setUp()

    def create_product(self):
        self.env['product.product'].create({
            "name": 'TEST',
            "type": 'service',
            "purchase_ok": False,
            "sale_ok": False,
            "tms_product_category": 'move',
        })

    def test_10_product_template_unique_product_per_category(self):
        with self.assertRaises(
                exceptions.ValidationError):
            self.create_product()

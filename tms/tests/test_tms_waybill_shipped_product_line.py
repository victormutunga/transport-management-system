# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestTmsWaybillShippedProductLine(TransactionCase):
    """
        test tms waybill shipped product line
    """

    def setUp(self):
        super(TestTmsWaybillShippedProductLine, self).setUp()
        self.product = self.env.ref('product.product_product_0')
        self.product1 = self.env.ref('product.product_product_1')
        self.shipped_product = self.env['tms.waybill.shipped.product.line']

    def create_shipped_product(self, name, product_id, product_uom):
        shipped_product = self.shipped_product.create({
            'name': name,
            'product_id': product_id,
            'product_uom': product_uom,
            'product_uom_qty': 1.0
        })
        return shipped_product

    def test_10_onchange_product_id(self):
        shipp_prod = self.create_shipped_product(
            self.product.name, self.product.id, self.product.uom_id.id)
        shipp_prod.write({'product_id': self.product1.id})
        shipp_prod._onchange_product_id()
        self.assertEquals(
            shipp_prod.name, self.product1.name,
            "Name is not changed")

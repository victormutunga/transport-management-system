# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestTmsWaybill(TransactionCase):

    def setUp(self):
        super(TestTmsWaybill, self).setUp()
        self.waybill = self.env['tms.waybill']
        self.operating_unit = self.env.ref(
            'operating_unit.main_operating_unit')
        self.customer = self.env.ref('base.res_partner_2')
        self.customer3 = self.env.ref('base.res_partner_3')
        self.departure = self.env.ref('base.res_partner_address_31')
        self.arrival = self.env.ref('base.res_partner_address_3')
        self.freight = self.env.ref('tms.product_freight')
        self.insurance = self.env.ref('tms.product_insurance')
        self.travel_id1 = self.env.ref("tms.tms_travel_01")
        self.transportable = self.env.ref('tms.tms_transportable_01')

    def create_waybill(self):
        return self.waybill.create({
            'operating_unit_id': self.operating_unit.id,
            'partner_id': self.customer.id,
            'departure_address_id': self.departure.id,
            'arrival_address_id': self.arrival.id,
            'travel_ids': [(4, self.travel_id1.id)],
            'partner_invoice_id': self.customer.id,
            'partner_order_id': self.customer.id,
            'transportable_line_ids': [(0, 0, {
                'transportable_id': self.transportable.id,
                'name': self.transportable.name,
                'transportable_uom_id': self.transportable.uom_id.id,
                'quantity': 10
            })],
            'customer_factor_ids': [(0, 0, {
                'factor_type': 'travel',
                'name': 'Travel',
                'fixed_amount': 100.00,
                'category': 'customer',
            })],
        })

    def test_10_tms_waybill_onchange_partner_id(self):
        waybill = self.create_waybill()
        waybill.partner_id = self.customer3.id
        waybill.onchange_partner_id()
        address = self.customer3.address_get(
            ['invoice', 'contact']).get('contact', False)
        self.assertEqual(waybill.partner_order_id.id, address)
        self.assertEqual(waybill.partner_invoice_id.id, address)

    def test_20_tms_waybill_compute_invoice_paid(self):
        waybill = self.create_waybill()
        waybill.action_confirm()
        wizard = self.env['tms.wizard.invoice'].with_context({
            'active_model': 'tms.waybill',
            'active_ids': [waybill.id]}).create({})
        wizard.make_invoices()
        waybill.invoice_id.state = "paid"
        waybill._compute_invoice_paid()
        self.assertEqual(waybill.invoice_paid, True)

    def test_30_tms_waybill_onchange_waybill_line_ids(self):
        waybill = self.create_waybill()
        waybill._onchange_waybill_line_ids()
        self.assertEqual(waybill.waybill_line_ids.unit_price, 100.0)

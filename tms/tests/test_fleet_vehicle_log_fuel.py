# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestFleetVehicleLogFuel(TransactionCase):

    def setUp(self):
        super(TestFleetVehicleLogFuel, self).setUp()
        self.fuel_log = self.env.ref('tms.tms_fuel_log_01')
        self.fuel_log2 = self.env.ref('tms.tms_fuel_log_02')

    def test_10_fleet_vehicle_log_fuel(self):
        self.fuel_log.price_subtotal = 100
        self.fuel_log.product_qty = 10
        price = self.fuel_log.price_unit
        self.assertEqual(price, 10)

        self.fuel_log.price_subtotal = 0
        self.fuel_log.product_qty = 0
        price = self.fuel_log.price_unit
        self.assertEqual(price, 0)
